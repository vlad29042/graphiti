"""
N8n WebHook Client for Graphiti
Redirects LLM calls to n8n workflow for processing
"""

import os
import json
import logging
import typing
from typing import Any
import asyncio
import httpx
from pydantic import BaseModel

from ..prompts.models import Message
from .client import LLMClient
from .config import LLMConfig, ModelSize

logger = logging.getLogger(__name__)


class N8nClient(LLMClient):
    """
    Client that redirects LLM calls to n8n webhook for processing.
    This allows n8n workflows to handle prompt processing with custom logic.
    """
    
    def __init__(
        self,
        config: LLMConfig | None = None,
        cache_enabled: bool = False,
        webhook_url: str | None = None,
        fallback_webhook_url: str | None = None,
        **kwargs
    ):
        super().__init__(config, cache_enabled, **kwargs)
        self.webhook_url = webhook_url or os.getenv('N8N_WEBHOOK_URL')
        self.fallback_webhook_url = fallback_webhook_url or os.getenv('N8N_FALLBACK_WEBHOOK_URL')
        
        if not self.webhook_url:
            raise ValueError("N8N_WEBHOOK_URL must be provided either as parameter or environment variable")
        
        self.timeout = int(os.getenv('N8N_TIMEOUT', '300'))  # 5 minutes default
        self.retry_on_primary = int(os.getenv('N8N_RETRY_PRIMARY', '2'))  # retries before switching to fallback
        
        logger.info(f"N8n client initialized with webhook: {self.webhook_url}")
        if self.fallback_webhook_url:
            logger.info(f"Fallback webhook configured: {self.fallback_webhook_url}")

    async def _generate_response(
        self,
        messages: list[Message],
        response_model: type[BaseModel] | None = None,
        max_tokens: int = 16384,
        model_size: ModelSize = ModelSize.medium,
    ) -> dict[str, Any]:
        """
        Send prompt to n8n webhook for processing.
        
        The webhook payload includes:
        - messages: The prompt messages
        - response_model: The expected response schema
        - context: Additional context about the operation
        """
        
        # Prepare webhook payload
        payload = {
            "messages": [msg.model_dump() for msg in messages],
            "response_model": response_model.model_json_schema() if response_model else None,
            "response_model_name": response_model.__name__ if response_model else None,
            "max_tokens": max_tokens,
            "model_size": model_size.value,
            "config": {
                "temperature": self.config.temperature if self.config else 0,
                "model": self.model
            }
        }
        
        # Extract operation context from system message
        if messages and messages[0].role == "system":
            system_content = messages[0].content.lower()
            if "extracts entity nodes from conversational messages" in system_content:
                payload["operation"] = "extract_nodes"
            elif "extracts entity nodes from text" in system_content:
                payload["operation"] = "extract_nodes"
            elif "extracts entity nodes from json" in system_content:
                payload["operation"] = "extract_nodes_json"
            elif "de-duplicates nodes" in system_content:
                payload["operation"] = "dedupe_nodes" 
            elif "extract fact triples" in system_content:
                payload["operation"] = "extract_edges"
            elif "de-duplicates edges" in system_content:
                payload["operation"] = "dedupe_edges"
            elif "determines which facts contradict" in system_content:
                payload["operation"] = "invalidate_edges"
            elif "determines which entities have not been extracted" in system_content:
                payload["operation"] = "extract_nodes_reflexion"
            elif "determine which facts have not been extracted" in system_content:
                payload["operation"] = "extract_edges_reflexion"
            elif "classifies entity nodes" in system_content:
                payload["operation"] = "classify_nodes"
            elif "determines whether or not a new entity is a duplicate" in system_content:
                payload["operation"] = "dedupe_single_node"
            else:
                payload["operation"] = "unknown"
        
        logger.debug(f"Sending to n8n webhook: operation={payload.get('operation')}")
        
        # Try primary webhook first
        webhooks_to_try = [(self.webhook_url, "primary")]
        if self.fallback_webhook_url:
            webhooks_to_try.append((self.fallback_webhook_url, "fallback"))
        
        last_error = None
        
        for webhook_url, webhook_type in webhooks_to_try:
            # Multiple attempts for primary webhook
            attempts = self.retry_on_primary if webhook_type == "primary" else 1
            
            for attempt in range(attempts):
                try:
                    logger.debug(f"Attempting {webhook_type} webhook (attempt {attempt + 1}/{attempts}): {webhook_url}")
                    
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            webhook_url,
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        )
                        response.raise_for_status()
                        
                        result = response.json()
                        
                        # n8n should return the response in the expected format
                        if "error" in result:
                            raise Exception(f"n8n workflow error: {result['error']}")
                        
                        if webhook_type == "fallback":
                            logger.warning(f"Successfully used fallback webhook for operation: {payload.get('operation')}")
                        
                        return result.get("response", {})
                        
                except httpx.TimeoutError as e:
                    last_error = e
                    logger.warning(f"{webhook_type} webhook timeout after {self.timeout}s (attempt {attempt + 1}/{attempts})")
                except httpx.HTTPStatusError as e:
                    last_error = e
                    logger.warning(f"{webhook_type} webhook HTTP error: {e.response.status_code} (attempt {attempt + 1}/{attempts})")
                except Exception as e:
                    last_error = e
                    logger.warning(f"{webhook_type} webhook error: {str(e)} (attempt {attempt + 1}/{attempts})")
                
                # Small delay between retries
                if attempt < attempts - 1:
                    await asyncio.sleep(1)
        
        # If we get here, all attempts failed
        logger.error(f"All webhook attempts failed. Last error: {str(last_error)}")
        raise Exception(f"Failed to process through n8n after all attempts. Last error: {str(last_error)}")
"""
Factory for creating LLM clients based on environment configuration
"""

import os
import logging
from typing import Optional

from .client import LLMClient
from .openai_client import OpenAIClient
from .n8n_client import N8nClient
from .config import LLMConfig

logger = logging.getLogger(__name__)


def create_llm_client(
    provider: str | None = None,
    config: LLMConfig | None = None,
    cache_enabled: bool = False,
    **kwargs
) -> LLMClient:
    """
    Factory function to create LLM client based on provider or environment settings.
    
    Parameters:
    -----------
    provider : str | None
        The LLM provider to use. If None, checks LLM_PROVIDER env var.
        Options: 'openai', 'anthropic', 'gemini', 'groq', 'n8n'
    config : LLMConfig | None
        Configuration for the LLM client
    cache_enabled : bool
        Whether to enable response caching
    **kwargs
        Additional provider-specific parameters
        
    Returns:
    --------
    LLMClient
        An instance of the appropriate LLM client
        
    Environment Variables:
    ---------------------
    LLM_PROVIDER : str
        The default LLM provider if not specified
    USE_N8N_PROCESSING : str
        If 'true', forces use of n8n client regardless of provider
    N8N_WEBHOOK_URL : str
        Required when using n8n provider
    """
    
    # Check if n8n processing is forced
    use_n8n = os.getenv('USE_N8N_PROCESSING', '').lower() == 'true'
    if use_n8n:
        logger.info("N8n processing is enabled via USE_N8N_PROCESSING env var")
        provider = 'n8n'
    
    # Get provider from env if not specified
    if provider is None:
        provider = os.getenv('LLM_PROVIDER', 'openai').lower()
    
    logger.info(f"Creating LLM client for provider: {provider}")
    
    # Create appropriate client
    if provider == 'n8n':
        webhook_url = kwargs.get('webhook_url') or os.getenv('N8N_WEBHOOK_URL')
        fallback_webhook_url = kwargs.get('fallback_webhook_url') or os.getenv('N8N_FALLBACK_WEBHOOK_URL')
        if not webhook_url:
            raise ValueError("N8N_WEBHOOK_URL must be set when using n8n provider")
        return N8nClient(
            config=config, 
            cache_enabled=cache_enabled, 
            webhook_url=webhook_url,
            fallback_webhook_url=fallback_webhook_url,
            **kwargs
        )
    
    elif provider == 'openai':
        return OpenAIClient(config=config, cache_enabled=cache_enabled, **kwargs)
    
    elif provider == 'anthropic':
        try:
            from .anthropic_client import AnthropicClient
            return AnthropicClient(config=config, cache_enabled=cache_enabled, **kwargs)
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install graphiti-core[anthropic]")
    
    elif provider == 'gemini':
        try:
            from .gemini_client import GeminiClient
            return GeminiClient(config=config, cache_enabled=cache_enabled, **kwargs)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install graphiti-core[gemini]")
    
    elif provider == 'groq':
        try:
            from .groq_client import GroqClient
            return GroqClient(config=config, cache_enabled=cache_enabled, **kwargs)
        except ImportError:
            raise ImportError("groq package not installed. Install with: pip install graphiti-core[groq]")
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Supported: openai, anthropic, gemini, groq, n8n")
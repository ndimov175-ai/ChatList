"""
Factory for creating API clients based on model configuration.
"""
import logging
from typing import Optional, Dict, Any

from chatlist.models.base_client import BaseAPIClient
from chatlist.models.openai_client import OpenAIClient
from chatlist.models.anthropic_client import AnthropicClient
from chatlist.models.google_client import GoogleClient
from chatlist.models.openrouter_client import OpenRouterClient
from chatlist.config.settings import config

logger = logging.getLogger(__name__)


class ClientFactory:
    """Factory for creating API clients."""

    @staticmethod
    def create_client(
        model_name: str,
        api_url: str,
        api_key_var: str,
        **kwargs
    ) -> Optional[BaseAPIClient]:
        """
        Create an API client based on model configuration.

        Args:
            model_name: Name of the model
            api_url: API endpoint URL
            api_key_var: Name of environment variable containing API key
            **kwargs: Additional parameters for the client

        Returns:
            API client instance or None if creation fails
        """
        # Get API key from config
        # Extract provider name from api_key_var
        # Examples: "OPENROUTER_API_KEY" -> "openrouter", "OPENAI_API_KEY" -> "openai"
        provider = api_key_var.lower()
        if provider.endswith('_api_key'):
            provider = provider[:-8]  # Remove "_api_key" suffix
        elif provider.endswith('api_key'):
            provider = provider[:-7]  # Remove "api_key" suffix
        
        api_key = config.get_api_key(provider)

        if not api_key:
            logger.warning(f"API key not found for {api_key_var} (extracted provider: '{provider}')")
            logger.debug(f"Available API keys: openai={bool(config.openai_api_key)}, "
                        f"anthropic={bool(config.anthropic_api_key)}, "
                        f"google={bool(config.google_api_key)}, "
                        f"openrouter={bool(config.openrouter_api_key)}")
            return None
        
        logger.debug(f"Creating client for {model_name} with provider '{provider}' (key length: {len(api_key)})")

        # Determine client type based on API URL or model name
        api_url_lower = api_url.lower()
        model_name_lower = model_name.lower()

        try:
            if 'openai.com' in api_url_lower or 'gpt' in model_name_lower:
                return OpenAIClient(
                    api_url=api_url,
                    api_key=api_key,
                    model_name=model_name,
                    **kwargs
                )
            elif 'anthropic.com' in api_url_lower or 'claude' in model_name_lower:
                return AnthropicClient(
                    api_url=api_url,
                    api_key=api_key,
                    model_name=model_name,
                    **kwargs
                )
            elif 'openrouter.ai' in api_url_lower or 'openrouter' in model_name_lower:
                return OpenRouterClient(
                    api_url=api_url,
                    api_key=api_key,
                    model_name=model_name,
                    **kwargs
                )
            elif 'googleapis.com' in api_url_lower or 'gemini' in model_name_lower:
                return GoogleClient(
                    api_url=api_url,
                    api_key=api_key,
                    model_name=model_name,
                    **kwargs
                )
            else:
                # Try to create a generic client (fallback to OpenAI format)
                logger.warning(f"Unknown API type for {model_name}, using OpenAI format")
                return OpenAIClient(
                    api_url=api_url,
                    api_key=api_key,
                    model_name=model_name,
                    **kwargs
                )
        except Exception as e:
            logger.error(f"Error creating client for {model_name}: {e}")
            return None

    @staticmethod
    def create_client_from_model(model_data: Dict[str, Any], **kwargs) -> Optional[BaseAPIClient]:
        """
        Create an API client from model database record.

        Args:
            model_data: Dictionary with model data (name, api_url, api_key_var)
            **kwargs: Additional parameters for the client

        Returns:
            API client instance or None if creation fails
        """
        return ClientFactory.create_client(
            model_name=model_data.get('name', ''),
            api_url=model_data.get('api_url', ''),
            api_key_var=model_data.get('api_key_var', ''),
            **kwargs
        )


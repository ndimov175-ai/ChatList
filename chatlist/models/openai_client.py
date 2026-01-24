"""
OpenAI API client for GPT models.
"""
import logging
from typing import Optional, Dict, Any

from chatlist.models.base_client import BaseAPIClient, APIResponse

logger = logging.getLogger(__name__)


class OpenAIClient(BaseAPIClient):
    """Client for OpenAI GPT models."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize OpenAI client.

        Args:
            api_url: API endpoint URL
            api_key: OpenAI API key
            timeout: Request timeout in seconds
            model_name: Name of the model (e.g., "gpt-4", "gpt-3.5-turbo")
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        """
        super().__init__(api_url, api_key, timeout, model_name)
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def send_request(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> APIResponse:
        """
        Send a request to OpenAI API.

        Args:
            prompt: The prompt text to send
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens (overrides default)
            **kwargs: Additional parameters

        Returns:
            APIResponse object with the result
        """
        import time
        start_time = time.time()

        try:
            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.temperature
            max_toks = max_tokens if max_tokens is not None else self.max_tokens

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temp,
                "max_tokens": max_toks
            }

            # Add any additional parameters
            payload.update(kwargs)

            # Make request
            response = await self._make_request(
                method="POST",
                url=self.api_url,
                json_data=payload
            )

            response_data = response.json()
            response_time = time.time() - start_time

            # Extract response text
            choices = response_data.get("choices", [])
            if not choices:
                raise ValueError("No choices in API response")

            text = choices[0].get("message", {}).get("content", "")
            if not text:
                raise ValueError("Empty response from API")

            # Extract token usage
            usage = response_data.get("usage", {})
            tokens_used = usage.get("total_tokens")

            return APIResponse(
                text=text,
                response_time=response_time,
                tokens_used=tokens_used,
                model=self.model_name,
                raw_response=response_data
            )

        except Exception as e:
            response_time = time.time() - start_time
            return self._handle_error(e, f"OpenAI API ({self.model_name})")

    def _extract_tokens(self, response_data: Dict[str, Any]) -> Optional[int]:
        """Extract token usage from OpenAI response."""
        usage = response_data.get("usage", {})
        return usage.get("total_tokens")


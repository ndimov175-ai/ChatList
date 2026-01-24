"""
Anthropic API client for Claude models.
"""
import logging
import time
from typing import Optional, Dict, Any

from chatlist.models.base_client import BaseAPIClient, APIResponse

logger = logging.getLogger(__name__)


class AnthropicClient(BaseAPIClient):
    """Client for Anthropic Claude models."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        model_name: str = "claude-3-opus-20240229",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize Anthropic client.

        Args:
            api_url: API endpoint URL
            api_key: Anthropic API key
            timeout: Request timeout in seconds
            model_name: Name of the model (e.g., "claude-3-opus-20240229")
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        super().__init__(api_url, api_key, timeout, model_name)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Anthropic API."""
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key or '',
            'anthropic-version': '2023-06-01'
        }
        return headers

    async def send_request(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> APIResponse:
        """
        Send a request to Anthropic API.

        Args:
            prompt: The prompt text to send
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens (overrides default)
            **kwargs: Additional parameters

        Returns:
            APIResponse object with the result
        """
        start_time = time.time()

        try:
            # Use provided parameters or defaults
            temp = temperature if temperature is not None else self.temperature
            max_toks = max_tokens if max_tokens is not None else self.max_tokens

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "max_tokens": max_toks,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temp
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
            content = response_data.get("content", [])
            if not content:
                raise ValueError("No content in API response")

            text = content[0].get("text", "")
            if not text:
                raise ValueError("Empty response from API")

            # Extract token usage
            usage = response_data.get("usage", {})
            tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)

            return APIResponse(
                text=text,
                response_time=response_time,
                tokens_used=tokens_used,
                model=self.model_name,
                raw_response=response_data
            )

        except Exception as e:
            response_time = time.time() - start_time
            return self._handle_error(e, f"Anthropic API ({self.model_name})")

    def _extract_tokens(self, response_data: Dict[str, Any]) -> Optional[int]:
        """Extract token usage from Anthropic response."""
        usage = response_data.get("usage", {})
        return usage.get("input_tokens", 0) + usage.get("output_tokens", 0)


"""
Google Gemini API client.
"""
import logging
import time
from typing import Optional, Dict, Any

from chatlist.models.base_client import BaseAPIClient, APIResponse

logger = logging.getLogger(__name__)


class GoogleClient(BaseAPIClient):
    """Client for Google Gemini models."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        model_name: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize Google Gemini client.

        Args:
            api_url: API endpoint URL (should include API key as query param)
            api_key: Google API key
            timeout: Request timeout in seconds
            model_name: Name of the model (e.g., "gemini-pro")
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        # Google API uses API key in URL, not headers
        super().__init__(api_url, None, timeout, model_name)
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Google API."""
        return {
            'Content-Type': 'application/json',
        }

    def _get_url_with_key(self) -> str:
        """Get API URL with API key as query parameter."""
        if not self.api_key:
            return self.api_url

        # Check if URL already has query parameters
        separator = '&' if '?' in self.api_url else '?'
        return f"{self.api_url}{separator}key={self.api_key}"

    async def send_request(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> APIResponse:
        """
        Send a request to Google Gemini API.

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
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temp,
                    "maxOutputTokens": max_toks
                }
            }

            # Add any additional parameters
            payload.update(kwargs)

            # Get URL with API key
            url = self._get_url_with_key()

            # Make request
            response = await self._make_request(
                method="POST",
                url=url,
                json_data=payload
            )

            response_data = response.json()
            response_time = time.time() - start_time

            # Extract response text
            candidates = response_data.get("candidates", [])
            if not candidates:
                raise ValueError("No candidates in API response")

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if not parts:
                raise ValueError("No parts in API response")

            text = parts[0].get("text", "")
            if not text:
                raise ValueError("Empty response from API")

            # Extract token usage
            usage_metadata = response_data.get("usageMetadata", {})
            tokens_used = usage_metadata.get("totalTokenCount")

            return APIResponse(
                text=text,
                response_time=response_time,
                tokens_used=tokens_used,
                model=self.model_name,
                raw_response=response_data
            )

        except Exception as e:
            response_time = time.time() - start_time
            return self._handle_error(e, f"Google API ({self.model_name})")

    def _extract_tokens(self, response_data: Dict[str, Any]) -> Optional[int]:
        """Extract token usage from Google response."""
        usage_metadata = response_data.get("usageMetadata", {})
        return usage_metadata.get("totalTokenCount")


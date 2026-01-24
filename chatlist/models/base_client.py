"""
Base abstract API client for AI models.
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass

import httpx
from chatlist.config.settings import config

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Response from API client."""
    text: str
    response_time: float
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class BaseAPIClient(ABC):
    """Base abstract class for API clients."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        model_name: Optional[str] = None
    ):
        """
        Initialize API client.

        Args:
            api_url: API endpoint URL
            api_key: API key for authentication
            timeout: Request timeout in seconds
            model_name: Name of the model (for identification)
        """
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout or config.request_timeout
        self.model_name = model_name
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    @abstractmethod
    async def send_request(
        self,
        prompt: str,
        **kwargs
    ) -> APIResponse:
        """
        Send a request to the API.

        Args:
            prompt: The prompt text to send
            **kwargs: Additional parameters specific to the API

        Returns:
            APIResponse object with the result
        """
        pass

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for the request.

        Returns:
            Dictionary of headers
        """
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    def _handle_error(self, error: Exception, context: str = "") -> APIResponse:
        """
        Handle API errors and create error response.

        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred

        Returns:
            APIResponse with error information
        """
        error_msg = str(error)
        logger.error(f"API error {context}: {error_msg}")

        # Handle specific error types
        if isinstance(error, httpx.TimeoutException):
            error_msg = f"Request timeout after {self.timeout} seconds"
        elif isinstance(error, httpx.HTTPStatusError):
            status_code = error.response.status_code
            try:
                error_detail = error.response.json()
                error_msg = f"HTTP {status_code}: {error_detail}"
            except Exception:
                error_msg = f"HTTP {status_code}: {error.response.text[:200]}"
        elif isinstance(error, httpx.RequestError):
            error_msg = f"Request failed: {error_msg}"

        return APIResponse(
            text="",
            response_time=0.0,
            error=error_msg,
            model=self.model_name
        )

    def _extract_tokens(self, response_data: Dict[str, Any]) -> Optional[int]:
        """
        Extract token usage from API response.

        Args:
            response_data: Response data from API

        Returns:
            Number of tokens used or None
        """
        # Default implementation - subclasses should override
        return None

    async def _make_request(
        self,
        method: str,
        url: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            json_data: JSON data to send
            headers: Request headers

        Returns:
            HTTP response
        """
        if headers is None:
            headers = self._get_headers()

        response = await self.client.request(
            method=method,
            url=url,
            json=json_data,
            headers=headers
        )
        response.raise_for_status()
        return response


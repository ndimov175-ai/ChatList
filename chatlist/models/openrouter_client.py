"""
OpenRouter API client for accessing multiple AI models through a unified API.
"""
import asyncio
import logging
import time
import re
from typing import Optional, Dict, Any

import httpx
from chatlist.models.base_client import BaseAPIClient, APIResponse

logger = logging.getLogger(__name__)


class OpenRouterClient(BaseAPIClient):
    """Client for OpenRouter API (unified access to multiple models)."""

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        model_name: str = "openai/gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000  # Reduced default for free tier compatibility
    ):
        """
        Initialize OpenRouter client.

        Args:
            api_url: API endpoint URL (usually https://openrouter.ai/api/v1/chat/completions)
            api_key: OpenRouter API key
            timeout: Request timeout in seconds
            model_name: Name of the model (e.g., "openai/gpt-4", "anthropic/claude-3-opus")
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
        """
        super().__init__(api_url, api_key, timeout, model_name)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for OpenRouter API."""
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Authorization header is required for OpenRouter
        if not self.api_key:
            logger.error("OpenRouter API key is missing - cannot make request")
            raise ValueError("OpenRouter API key is required")
        
        # OpenRouter requires Bearer token in Authorization header
        headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Optional but recommended headers
        headers['HTTP-Referer'] = 'https://github.com/niki-sudo/ChatList'
        headers['X-Title'] = 'ChatList'
        
        return headers

    async def send_request(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> APIResponse:
        """
        Send a request to OpenRouter API.

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

        except httpx.HTTPStatusError as e:
            # Handle 402 Payment Required - try with reduced max_tokens
            if e.response.status_code == 402:
                try:
                    error_data = e.response.json()
                    error_info = error_data.get('error', {})
                    message = error_info.get('message', '')
                    
                    # Try to extract available tokens from error message
                    if 'can only afford' in message.lower():
                        # Extract number from message like "can only afford 1041"
                        match = re.search(r'can only afford (\d+)', message)
                        if match:
                            available_tokens = int(match.group(1))
                            # Retry with available tokens (with some margin)
                            safe_tokens = max(100, available_tokens - 50)
                            logger.warning(f"Retrying with reduced max_tokens: {safe_tokens} (was {max_toks})")
                            
                            payload['max_tokens'] = safe_tokens
                            response = await self._make_request(
                                method="POST",
                                url=self.api_url,
                                json_data=payload
                            )
                            response_data = response.json()
                            response_time = time.time() - start_time
                            
                            choices = response_data.get("choices", [])
                            if choices:
                                text = choices[0].get("message", {}).get("content", "")
                                usage = response_data.get("usage", {})
                                tokens_used = usage.get("total_tokens")
                                
                                return APIResponse(
                                    text=text,
                                    response_time=response_time,
                                    tokens_used=tokens_used,
                                    model=self.model_name,
                                    raw_response=response_data
                                )
                except Exception as retry_error:
                    logger.error(f"Retry failed: {retry_error}")
            
            # Handle 429 Rate Limiting - retry with exponential backoff
            elif e.response.status_code == 429:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Exponential backoff: 2^attempt seconds (1, 2, 4 seconds)
                        backoff_time = 2 ** attempt
                        logger.warning(f"Rate limited (429). Retrying in {backoff_time} seconds... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(backoff_time)
                        
                        response = await self._make_request(
                            method="POST",
                            url=self.api_url,
                            json_data=payload
                        )
                        response_data = response.json()
                        response_time = time.time() - start_time
                        
                        choices = response_data.get("choices", [])
                        if choices:
                            text = choices[0].get("message", {}).get("content", "")
                            usage = response_data.get("usage", {})
                            tokens_used = usage.get("total_tokens")
                            
                            logger.info(f"Rate limit retry successful after {backoff_time} seconds")
                            return APIResponse(
                                text=text,
                                response_time=response_time,
                                tokens_used=tokens_used,
                                model=self.model_name,
                                raw_response=response_data
                            )
                    except Exception as retry_error:
                        logger.error(f"Rate limit retry {attempt + 1} failed: {retry_error}")
                        if attempt == max_retries - 1:
                            # Final attempt failed
                            break
                
                # All retries failed
                logger.error(f"All rate limit retries failed for model {self.model_name}")
            
            # If retry failed or not a retryable error, handle normally
            response_time = time.time() - start_time
            return self._handle_error(e, f"OpenRouter API ({self.model_name})")
        
        except Exception as e:
            response_time = time.time() - start_time
            return self._handle_error(e, f"OpenRouter API ({self.model_name})")

    def _extract_tokens(self, response_data: Dict[str, Any]) -> Optional[int]:
        """Extract token usage from OpenRouter response."""
        usage = response_data.get("usage", {})
        return usage.get("total_tokens")


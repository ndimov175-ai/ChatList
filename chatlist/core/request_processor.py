"""
Request processor for coordinating concurrent API requests to multiple models.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from chatlist.models.base_client import BaseAPIClient, APIResponse
from chatlist.models.client_factory import ClientFactory
from chatlist.db.model_manager import ModelManager
from chatlist.config.settings import config

logger = logging.getLogger(__name__)


@dataclass
class RequestResult:
    """Result of a request to a single model."""
    model_id: int
    model_name: str
    response: APIResponse
    success: bool


class RequestProcessor:
    """Processes requests to multiple models concurrently."""

    def __init__(self, max_concurrent: Optional[int] = None):
        """
        Initialize request processor.

        Args:
            max_concurrent: Maximum number of concurrent requests
        """
        self.max_concurrent = max_concurrent or config.max_concurrent_requests
        self.clients: Dict[int, BaseAPIClient] = {}
        self._semaphore = asyncio.Semaphore(self.max_concurrent)
        self._current_tasks: List[asyncio.Task] = []
        self._cancelled = False

    async def _create_client(self, model_id: int) -> Optional[BaseAPIClient]:
        """
        Create or get cached client for a model.

        Args:
            model_id: ID of the model

        Returns:
            API client instance or None
        """
        if model_id in self.clients:
            return self.clients[model_id]

        model_data = ModelManager.get_by_id(model_id)
        if not model_data:
            logger.error(f"Model {model_id} not found")
            return None

        if not model_data.get('is_active'):
            logger.warning(f"Model {model_id} is not active")
            return None

        client = ClientFactory.create_client_from_model(model_data)
        if client:
            self.clients[model_id] = client

        return client

    async def _send_single_request(
        self,
        model_id: int,
        prompt: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> RequestResult:
        """
        Send a request to a single model.

        Args:
            model_id: ID of the model
            prompt: Prompt text
            progress_callback: Optional callback for progress updates

        Returns:
            RequestResult object
        """
        async with self._semaphore:
            # Check if cancelled
            if self._cancelled:
                raise asyncio.CancelledError()

            model_data = ModelManager.get_by_id(model_id)
            model_name = model_data.get('name', 'Unknown') if model_data else 'Unknown'

            if progress_callback:
                progress_callback(model_id, f"Sending request to {model_name}...")

            try:
                client = await self._create_client(model_id)
                if not client:
                    return RequestResult(
                        model_id=model_id,
                        model_name=model_name,
                        response=APIResponse(
                            text="",
                            response_time=0.0,
                            error="Failed to create API client"
                        ),
                        success=False
                    )

                if progress_callback:
                    progress_callback(model_id, f"Waiting for response from {model_name}...")

                # Check cancellation before sending
                if self._cancelled:
                    raise asyncio.CancelledError()

                response = await client.send_request(prompt)

                if progress_callback:
                    status = "Success" if not response.error else "Error"
                    progress_callback(model_id, f"{model_name}: {status}")

                return RequestResult(
                    model_id=model_id,
                    model_name=model_name,
                    response=response,
                    success=not bool(response.error)
                )

            except asyncio.CancelledError:
                logger.info(f"Request to model {model_id} was cancelled")
                return RequestResult(
                    model_id=model_id,
                    model_name=model_name,
                    response=APIResponse(
                        text="",
                        response_time=0.0,
                        error="Request cancelled"
                    ),
                    success=False
                )
            except Exception as e:
                logger.error(f"Error sending request to model {model_id}: {e}")
                return RequestResult(
                    model_id=model_id,
                    model_name=model_name,
                    response=APIResponse(
                        text="",
                        response_time=0.0,
                        error=str(e)
                    ),
                    success=False
                )

    async def send_to_models(
        self,
        model_ids: List[int],
        prompt: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[RequestResult]:
        """
        Send requests to multiple models concurrently.

        Args:
            model_ids: List of model IDs to send requests to
            prompt: Prompt text to send
            progress_callback: Optional callback for progress updates
                             (called with model_id, status_message)

        Returns:
            List of RequestResult objects
        """
        if not model_ids:
            logger.warning("No model IDs provided")
            return []

        # Reset cancellation flag
        self._cancelled = False
        self._current_tasks.clear()

        logger.info(f"Sending request to {len(model_ids)} model(s)")

        # Create tasks for all requests
        tasks = [
            asyncio.create_task(
                self._send_single_request(model_id, prompt, progress_callback)
            )
            for model_id in model_ids
        ]
        self._current_tasks = tasks

        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                model_id = model_ids[i]
                model_data = ModelManager.get_by_id(model_id)
                model_name = model_data.get('name', 'Unknown') if model_data else 'Unknown'
                error_msg = "Request cancelled" if isinstance(result, asyncio.CancelledError) else str(result)
                processed_results.append(RequestResult(
                    model_id=model_id,
                    model_name=model_name,
                    response=APIResponse(
                        text="",
                        response_time=0.0,
                        error=error_msg
                    ),
                    success=False
                ))
            else:
                processed_results.append(result)

        successful = sum(1 for r in processed_results if r.success)
        logger.info(f"Completed {successful}/{len(processed_results)} requests successfully")

        return processed_results

    def cancel_requests(self):
        """Cancel all pending requests."""
        self._cancelled = True
        for task in self._current_tasks:
            if not task.done():
                task.cancel()
        logger.info("Cancelled all pending requests")

    async def send_to_active_models(
        self,
        prompt: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[RequestResult]:
        """
        Send requests to all active models.

        Args:
            prompt: Prompt text to send
            progress_callback: Optional callback for progress updates

        Returns:
            List of RequestResult objects
        """
        active_models = ModelManager.get_active()
        model_ids = [model['id'] for model in active_models]
        return await self.send_to_models(model_ids, prompt, progress_callback)

    async def cleanup(self):
        """Cleanup all clients."""
        for client in self.clients.values():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing client: {e}")
        self.clients.clear()

    def __del__(self):
        """Cleanup on deletion."""
        # Try to cleanup clients
        if self.clients:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.cleanup())
                else:
                    loop.run_until_complete(self.cleanup())
            except Exception:
                pass


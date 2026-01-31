"""
Manager for prompt enhancement operations and database storage.
"""
import logging
from typing import Optional, List, Dict, Any

from chatlist.core.prompt_enhancer_client import PromptEnhancerClient
from chatlist.core.enhance_result import EnhanceResult
from chatlist.db.database_manager import db_manager
from chatlist.db.model_manager import ModelManager

logger = logging.getLogger(__name__)


class PromptEnhancerManager:
    """Manager for prompt enhancement operations."""

    def __init__(self):
        """Initialize the prompt enhancer manager."""
        self.client = PromptEnhancerClient()

    def enhance_prompt(
        self,
        prompt: str,
        model_id: int,
        enhancement_type: str = 'general'
    ) -> Optional[EnhanceResult]:
        """
        Enhance a prompt using the specified model.

        Args:
            prompt: The prompt to enhance
            model_id: ID of the model to use for enhancement
            enhancement_type: Type of enhancement

        Returns:
            EnhanceResult with enhancement data or None on error
        """
        # Get model details
        model = ModelManager.get_by_id(model_id)
        if not model:
            logger.error(f"Model {model_id} not found")
            return None

        # Use the model's API URL if available, otherwise use OpenRouter
        api_url = model.get('api_url', 'https://openrouter.ai/api/v1/chat/completions')

        # Call the client
        result = self.client.enhance_prompt(
            prompt=prompt,
            model_id=model_id,
            enhancement_type=enhancement_type,
            api_url=api_url
        )

        return result

    def save_enhancement(
        self,
        enhancement: EnhanceResult,
        prompt_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Save enhancement result to database.

        Args:
            enhancement: EnhanceResult to save
            prompt_id: Optional ID of the original prompt

        Returns:
            ID of saved enhancement or None on error
        """
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO prompt_enhancements (
                        original_prompt,
                        enhanced_prompt,
                        alternatives,
                        explanation,
                        recommendations,
                        model_id,
                        enhancement_type,
                        prompt_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    enhancement.original_prompt,
                    enhancement.enhanced_prompt,
                    '\n'.join(enhancement.alternatives) if enhancement.alternatives else '',
                    enhancement.explanation,
                    str(enhancement.recommendations),
                    enhancement.model_id,
                    enhancement.enhancement_type,
                    prompt_id
                ))
                enhancement_id = cursor.lastrowid
                logger.info(f"Saved enhancement with ID {enhancement_id}")
                return enhancement_id

        except Exception as e:
            logger.error(f"Error saving enhancement: {e}")
            return None

    def get_enhancement_history(
        self,
        prompt_id: Optional[int] = None,
        limit: int = 100
    ) -> List[EnhanceResult]:
        """
        Get enhancement history from database.

        Args:
            prompt_id: Optional prompt ID to filter by
            limit: Maximum number of results to return

        Returns:
            List of EnhanceResult objects
        """
        try:
            if prompt_id:
                rows = db_manager.fetch_all("""
                    SELECT * FROM prompt_enhancements
                    WHERE prompt_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (prompt_id, limit))
            else:
                rows = db_manager.fetch_all("""
                    SELECT * FROM prompt_enhancements
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

            results = []
            for row in rows:
                try:
                    result = EnhanceResult.from_dict(dict(row))
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Error converting row to EnhanceResult: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Error retrieving enhancement history: {e}")
            return []

    def get_enhancement_by_id(self, enhancement_id: int) -> Optional[EnhanceResult]:
        """
        Get a specific enhancement by ID.

        Args:
            enhancement_id: ID of the enhancement

        Returns:
            EnhanceResult or None if not found
        """
        try:
            row = db_manager.fetch_one(
                "SELECT * FROM prompt_enhancements WHERE id = ?",
                (enhancement_id,)
            )

            if row:
                return EnhanceResult.from_dict(dict(row))

            return None

        except Exception as e:
            logger.error(f"Error retrieving enhancement: {e}")
            return None

    def delete_enhancement(self, enhancement_id: int) -> bool:
        """
        Delete an enhancement from the database.

        Args:
            enhancement_id: ID of the enhancement to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM prompt_enhancements WHERE id = ?",
                    (enhancement_id,)
                )
                logger.info(f"Deleted enhancement {enhancement_id}")
                return True

        except Exception as e:
            logger.error(f"Error deleting enhancement: {e}")
            return False

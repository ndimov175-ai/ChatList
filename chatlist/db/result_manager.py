"""
Result manager for handling result CRUD operations.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from chatlist.db.database_manager import db_manager

logger = logging.getLogger(__name__)


class ResultManager:
    """Manages result operations in the database."""

    @staticmethod
    def create(
        prompt_id: int,
        model_id: int,
        response_text: str,
        response_time: Optional[float] = None,
        tokens_used: Optional[int] = None
    ) -> int:
        """
        Create a new result.

        Args:
            prompt_id: ID of the prompt
            model_id: ID of the model
            response_text: Text of the model's response
            response_time: Response time in seconds
            tokens_used: Number of tokens used

        Returns:
            ID of the created result
        """
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO results (prompt_id, model_id, response_text, response_time, tokens_used)
                VALUES (?, ?, ?, ?, ?)
            """, (prompt_id, model_id, response_text, response_time, tokens_used))
            result_id = cursor.lastrowid
            logger.info(f"Created result with ID {result_id} for prompt {prompt_id} and model {model_id}")
            return result_id

    @staticmethod
    def get_by_id(result_id: int) -> Optional[Dict[str, Any]]:
        """
        Get result by ID.

        Args:
            result_id: ID of the result

        Returns:
            Dictionary with result data or None
        """
        row = db_manager.fetch_one(
            "SELECT * FROM results WHERE id = ?",
            (result_id,)
        )
        if row:
            return ResultManager._row_to_dict(row)
        return None

    @staticmethod
    def get_by_prompt(prompt_id: int) -> List[Dict[str, Any]]:
        """
        Get all results for a specific prompt.

        Args:
            prompt_id: ID of the prompt

        Returns:
            List of result dictionaries
        """
        rows = db_manager.fetch_all(
            """
            SELECT r.*, m.name as model_name
            FROM results r
            JOIN models m ON r.model_id = m.id
            WHERE r.prompt_id = ?
            ORDER BY r.saved_at DESC
            """,
            (prompt_id,)
        )
        return [ResultManager._row_to_dict_with_model(row) for row in rows]

    @staticmethod
    def get_by_model(model_id: int) -> List[Dict[str, Any]]:
        """
        Get all results for a specific model.

        Args:
            model_id: ID of the model

        Returns:
            List of result dictionaries
        """
        rows = db_manager.fetch_all(
            """
            SELECT r.*, p.prompt_text
            FROM results r
            JOIN prompts p ON r.prompt_id = p.id
            WHERE r.model_id = ?
            ORDER BY r.saved_at DESC
            """,
            (model_id,)
        )
        return [ResultManager._row_to_dict_with_prompt(row) for row in rows]

    @staticmethod
    def get_by_prompt_and_model(
        prompt_id: int,
        model_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get result for a specific prompt and model combination.

        Args:
            prompt_id: ID of the prompt
            model_id: ID of the model

        Returns:
            Dictionary with result data or None
        """
        row = db_manager.fetch_one(
            """
            SELECT r.*, m.name as model_name, p.prompt_text
            FROM results r
            JOIN models m ON r.model_id = m.id
            JOIN prompts p ON r.prompt_id = p.id
            WHERE r.prompt_id = ? AND r.model_id = ?
            ORDER BY r.saved_at DESC
            LIMIT 1
            """,
            (prompt_id, model_id)
        )
        if row:
            return ResultManager._row_to_dict_full(row)
        return None

    @staticmethod
    def get_all(
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all results.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of result dictionaries
        """
        query = """
            SELECT r.*, m.name as model_name, p.prompt_text
            FROM results r
            JOIN models m ON r.model_id = m.id
            JOIN prompts p ON r.prompt_id = p.id
            ORDER BY r.saved_at DESC
        """
        params = []

        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        elif offset:
            query += " OFFSET ?"
            params.append(offset)

        rows = db_manager.fetch_all(query, tuple(params) if params else None)
        return [ResultManager._row_to_dict_full(row) for row in rows]

    @staticmethod
    def update(
        result_id: int,
        response_text: Optional[str] = None,
        response_time: Optional[float] = None,
        tokens_used: Optional[int] = None
    ) -> bool:
        """
        Update a result.

        Args:
            result_id: ID of the result to update
            response_text: New response text (optional)
            response_time: New response time (optional)
            tokens_used: New tokens used count (optional)

        Returns:
            True if update was successful, False otherwise
        """
        updates = []
        params = []

        if response_text is not None:
            updates.append("response_text = ?")
            params.append(response_text)

        if response_time is not None:
            updates.append("response_time = ?")
            params.append(response_time)

        if tokens_used is not None:
            updates.append("tokens_used = ?")
            params.append(tokens_used)

        if not updates:
            return False

        params.append(result_id)
        query = f"UPDATE results SET {', '.join(updates)} WHERE id = ?"

        try:
            db_manager.execute(query, tuple(params))
            logger.info(f"Updated result with ID {result_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating result {result_id}: {e}")
            return False

    @staticmethod
    def delete(result_id: int) -> bool:
        """
        Delete a result.

        Args:
            result_id: ID of the result to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            db_manager.execute("DELETE FROM results WHERE id = ?", (result_id,))
            logger.info(f"Deleted result with ID {result_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting result {result_id}: {e}")
            return False

    @staticmethod
    def delete_by_prompt(prompt_id: int) -> int:
        """
        Delete all results for a specific prompt.

        Args:
            prompt_id: ID of the prompt

        Returns:
            Number of deleted results
        """
        try:
            count = db_manager.execute(
                "DELETE FROM results WHERE prompt_id = ?",
                (prompt_id,)
            )
            logger.info(f"Deleted {count} result(s) for prompt {prompt_id}")
            return count
        except Exception as e:
            logger.error(f"Error deleting results for prompt {prompt_id}: {e}")
            return 0

    @staticmethod
    def _row_to_dict(row) -> Dict[str, Any]:
        """Convert database row to dictionary (basic)."""
        return {
            'id': row['id'],
            'prompt_id': row['prompt_id'],
            'model_id': row['model_id'],
            'response_text': row['response_text'],
            'response_time': row['response_time'],
            'tokens_used': row['tokens_used'],
            'saved_at': row['saved_at']
        }

    @staticmethod
    def _row_to_dict_with_model(row) -> Dict[str, Any]:
        """Convert database row to dictionary with model name."""
        result = ResultManager._row_to_dict(row)
        result['model_name'] = row.get('model_name', '')
        return result

    @staticmethod
    def _row_to_dict_with_prompt(row) -> Dict[str, Any]:
        """Convert database row to dictionary with prompt text."""
        result = ResultManager._row_to_dict(row)
        result['prompt_text'] = row.get('prompt_text', '')
        return result

    @staticmethod
    def _row_to_dict_full(row) -> Dict[str, Any]:
        """Convert database row to dictionary with all related data."""
        result = ResultManager._row_to_dict(row)
        result['model_name'] = row.get('model_name', '')
        result['prompt_text'] = row.get('prompt_text', '')
        return result


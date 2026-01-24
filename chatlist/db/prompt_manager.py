"""
Prompt manager for handling prompt CRUD operations.
"""
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from chatlist.db.database_manager import db_manager

logger = logging.getLogger(__name__)


class PromptManager:
    """Manages prompt operations in the database."""

    @staticmethod
    def create(
        prompt_text: str,
        tags: Optional[List[str]] = None,
        is_favorite: bool = False
    ) -> int:
        """
        Create a new prompt.

        Args:
            prompt_text: Text of the prompt
            tags: List of tags for categorization
            is_favorite: Whether the prompt is marked as favorite

        Returns:
            ID of the created prompt
        """
        tags_json = json.dumps(tags or [])
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO prompts (prompt_text, tags, is_favorite)
                VALUES (?, ?, ?)
            """, (prompt_text, tags_json, 1 if is_favorite else 0))
            prompt_id = cursor.lastrowid
            logger.info(f"Created prompt with ID {prompt_id}")
            return prompt_id

    @staticmethod
    def get_by_id(prompt_id: int) -> Optional[Dict[str, Any]]:
        """
        Get prompt by ID.

        Args:
            prompt_id: ID of the prompt

        Returns:
            Dictionary with prompt data or None
        """
        row = db_manager.fetch_one(
            "SELECT * FROM prompts WHERE id = ?",
            (prompt_id,)
        )
        if row:
            return PromptManager._row_to_dict(row)
        return None

    @staticmethod
    def get_all(
        limit: Optional[int] = None,
        offset: int = 0,
        favorite_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all prompts.

        Args:
            limit: Maximum number of prompts to return
            offset: Number of prompts to skip
            favorite_only: If True, return only favorite prompts

        Returns:
            List of prompt dictionaries
        """
        query = "SELECT * FROM prompts"
        params = []

        if favorite_only:
            query += " WHERE is_favorite = 1"

        query += " ORDER BY date_created DESC"

        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        elif offset:
            query += " OFFSET ?"
            params.append(offset)

        rows = db_manager.fetch_all(query, tuple(params) if params else None)
        return [PromptManager._row_to_dict(row) for row in rows]

    @staticmethod
    def search_by_text(search_text: str) -> List[Dict[str, Any]]:
        """
        Search prompts by text content.

        Args:
            search_text: Text to search for

        Returns:
            List of matching prompt dictionaries
        """
        rows = db_manager.fetch_all(
            "SELECT * FROM prompts WHERE prompt_text LIKE ? ORDER BY date_created DESC",
            (f"%{search_text}%",)
        )
        return [PromptManager._row_to_dict(row) for row in rows]

    @staticmethod
    def search_by_tags(tags: List[str]) -> List[Dict[str, Any]]:
        """
        Search prompts by tags.

        Args:
            tags: List of tags to search for

        Returns:
            List of matching prompt dictionaries
        """
        # Get all prompts and filter by tags
        all_prompts = PromptManager.get_all()
        matching_prompts = []

        for prompt in all_prompts:
            prompt_tags = prompt.get('tags', [])
            if any(tag in prompt_tags for tag in tags):
                matching_prompts.append(prompt)

        return matching_prompts

    @staticmethod
    def update(
        prompt_id: int,
        prompt_text: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_favorite: Optional[bool] = None
    ) -> bool:
        """
        Update a prompt.

        Args:
            prompt_id: ID of the prompt to update
            prompt_text: New prompt text (optional)
            tags: New tags (optional)
            is_favorite: New favorite status (optional)

        Returns:
            True if update was successful, False otherwise
        """
        updates = []
        params = []

        if prompt_text is not None:
            updates.append("prompt_text = ?")
            params.append(prompt_text)

        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps(tags))

        if is_favorite is not None:
            updates.append("is_favorite = ?")
            params.append(1 if is_favorite else 0)

        if not updates:
            return False

        params.append(prompt_id)
        query = f"UPDATE prompts SET {', '.join(updates)} WHERE id = ?"

        try:
            db_manager.execute(query, tuple(params))
            logger.info(f"Updated prompt with ID {prompt_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating prompt {prompt_id}: {e}")
            return False

    @staticmethod
    def delete(prompt_id: int) -> bool:
        """
        Delete a prompt.

        Args:
            prompt_id: ID of the prompt to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            db_manager.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
            logger.info(f"Deleted prompt with ID {prompt_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting prompt {prompt_id}: {e}")
            return False

    @staticmethod
    def toggle_favorite(prompt_id: int) -> bool:
        """
        Toggle favorite status of a prompt.

        Args:
            prompt_id: ID of the prompt

        Returns:
            True if toggle was successful, False otherwise
        """
        prompt = PromptManager.get_by_id(prompt_id)
        if not prompt:
            return False

        new_status = not prompt.get('is_favorite', False)
        return PromptManager.update(prompt_id, is_favorite=new_status)

    @staticmethod
    def _row_to_dict(row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        return {
            'id': row['id'],
            'date_created': row['date_created'],
            'prompt_text': row['prompt_text'],
            'tags': json.loads(row['tags']) if row['tags'] else [],
            'is_favorite': bool(row['is_favorite'])
        }


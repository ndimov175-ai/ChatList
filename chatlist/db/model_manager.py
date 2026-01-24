"""
Model manager for handling AI model CRUD operations.
"""
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from chatlist.db.database_manager import db_manager

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages AI model operations in the database."""

    @staticmethod
    def create(
        name: str,
        api_url: str,
        api_key_var: str,
        is_active: bool = True
    ) -> int:
        """
        Create a new model.

        Args:
            name: Name of the model
            api_url: API endpoint URL
            api_key_var: Name of environment variable containing API key
            is_active: Whether the model is active for requests

        Returns:
            ID of the created model
        """
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO models (name, api_url, api_key_var, is_active)
                VALUES (?, ?, ?, ?)
            """, (name, api_url, api_key_var, 1 if is_active else 0))
            model_id = cursor.lastrowid
            logger.info(f"Created model '{name}' with ID {model_id}")
            return model_id

    @staticmethod
    def get_by_id(model_id: int) -> Optional[Dict[str, Any]]:
        """
        Get model by ID.

        Args:
            model_id: ID of the model

        Returns:
            Dictionary with model data or None
        """
        row = db_manager.fetch_one(
            "SELECT * FROM models WHERE id = ?",
            (model_id,)
        )
        if row:
            return ModelManager._row_to_dict(row)
        return None

    @staticmethod
    def get_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        Get model by name.

        Args:
            name: Name of the model

        Returns:
            Dictionary with model data or None
        """
        row = db_manager.fetch_one(
            "SELECT * FROM models WHERE name = ?",
            (name,)
        )
        if row:
            return ModelManager._row_to_dict(row)
        return None

    @staticmethod
    def get_all(active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all models.

        Args:
            active_only: If True, return only active models

        Returns:
            List of model dictionaries
        """
        query = "SELECT * FROM models"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"

        rows = db_manager.fetch_all(query)
        return [ModelManager._row_to_dict(row) for row in rows]

    @staticmethod
    def get_active() -> List[Dict[str, Any]]:
        """
        Get all active models.

        Returns:
            List of active model dictionaries
        """
        return ModelManager.get_all(active_only=True)

    @staticmethod
    def update(
        model_id: int,
        name: Optional[str] = None,
        api_url: Optional[str] = None,
        api_key_var: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        Update a model.

        Args:
            model_id: ID of the model to update
            name: New name (optional)
            api_url: New API URL (optional)
            api_key_var: New API key variable name (optional)
            is_active: New active status (optional)

        Returns:
            True if update was successful, False otherwise
        """
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if api_url is not None:
            updates.append("api_url = ?")
            params.append(api_url)

        if api_key_var is not None:
            updates.append("api_key_var = ?")
            params.append(api_key_var)

        if is_active is not None:
            updates.append("is_active = ?")
            params.append(1 if is_active else 0)

        if not updates:
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(model_id)
        query = f"UPDATE models SET {', '.join(updates)} WHERE id = ?"

        try:
            db_manager.execute(query, tuple(params))
            logger.info(f"Updated model with ID {model_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating model {model_id}: {e}")
            return False

    @staticmethod
    def delete(model_id: int) -> bool:
        """
        Delete a model.

        Args:
            model_id: ID of the model to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            db_manager.execute("DELETE FROM models WHERE id = ?", (model_id,))
            logger.info(f"Deleted model with ID {model_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting model {model_id}: {e}")
            return False

    @staticmethod
    def toggle_active(model_id: int) -> bool:
        """
        Toggle active status of a model.

        Args:
            model_id: ID of the model

        Returns:
            True if toggle was successful, False otherwise
        """
        model = ModelManager.get_by_id(model_id)
        if not model:
            return False

        new_status = not model.get('is_active', False)
        return ModelManager.update(model_id, is_active=new_status)

    @staticmethod
    def _row_to_dict(row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        return {
            'id': row['id'],
            'name': row['name'],
            'api_url': row['api_url'],
            'api_key_var': row['api_key_var'],
            'is_active': bool(row['is_active']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        }


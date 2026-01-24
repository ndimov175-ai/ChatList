"""
Settings manager for handling application settings CRUD operations.
"""
import json
import logging
from typing import Optional, Dict, Any, Union

from chatlist.db.database_manager import db_manager

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manages application settings operations in the database."""

    @staticmethod
    def set(
        setting_key: str,
        setting_value: Union[str, int, float, bool, dict, list],
        setting_type: Optional[str] = None
    ) -> bool:
        """
        Set a setting value.

        Args:
            setting_key: Key of the setting
            setting_value: Value of the setting
            setting_type: Type of the value (auto-detected if None)

        Returns:
            True if setting was successful, False otherwise
        """
        # Auto-detect type if not provided
        if setting_type is None:
            if isinstance(setting_value, bool):
                setting_type = 'bool'
            elif isinstance(setting_value, int):
                setting_type = 'int'
            elif isinstance(setting_value, float):
                setting_type = 'float'
            elif isinstance(setting_value, (dict, list)):
                setting_type = 'json'
            else:
                setting_type = 'string'

        # Convert value to string representation
        if setting_type == 'json':
            value_str = json.dumps(setting_value)
        else:
            value_str = str(setting_value)

        try:
            # Try to update existing setting
            rowcount = db_manager.execute(
                """
                UPDATE settings
                SET setting_value = ?, setting_type = ?, updated_at = CURRENT_TIMESTAMP
                WHERE setting_key = ?
                """,
                (value_str, setting_type, setting_key)
            )

            # If no rows were updated, insert new setting
            if rowcount == 0:
                with db_manager.get_connection() as conn:
                    conn.execute("""
                        INSERT INTO settings (setting_key, setting_value, setting_type)
                        VALUES (?, ?, ?)
                    """, (setting_key, value_str, setting_type))

            logger.info(f"Set setting '{setting_key}' = {value_str} (type: {setting_type})")
            return True
        except Exception as e:
            logger.error(f"Error setting setting '{setting_key}': {e}")
            return False

    @staticmethod
    def get(
        setting_key: str,
        default: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Get a setting value.

        Args:
            setting_key: Key of the setting
            default: Default value if setting doesn't exist

        Returns:
            Setting value or default
        """
        row = db_manager.fetch_one(
            "SELECT * FROM settings WHERE setting_key = ?",
            (setting_key,)
        )

        if not row:
            return default

        return SettingsManager._parse_value(row['setting_value'], row['setting_type'])

    @staticmethod
    def get_all() -> Dict[str, Any]:
        """
        Get all settings.

        Returns:
            Dictionary of all settings
        """
        rows = db_manager.fetch_all("SELECT * FROM settings")
        settings = {}
        for row in rows:
            settings[row['setting_key']] = SettingsManager._parse_value(
                row['setting_value'],
                row['setting_type']
            )
        return settings

    @staticmethod
    def delete(setting_key: str) -> bool:
        """
        Delete a setting.

        Args:
            setting_key: Key of the setting to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            db_manager.execute(
                "DELETE FROM settings WHERE setting_key = ?",
                (setting_key,)
            )
            logger.info(f"Deleted setting '{setting_key}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting setting '{setting_key}': {e}")
            return False

    @staticmethod
    def exists(setting_key: str) -> bool:
        """
        Check if a setting exists.

        Args:
            setting_key: Key of the setting

        Returns:
            True if setting exists, False otherwise
        """
        row = db_manager.fetch_one(
            "SELECT 1 FROM settings WHERE setting_key = ?",
            (setting_key,)
        )
        return row is not None

    @staticmethod
    def _parse_value(value_str: str, value_type: str) -> Any:
        """
        Parse setting value from string based on type.

        Args:
            value_str: String representation of the value
            value_type: Type of the value

        Returns:
            Parsed value
        """
        if value_type == 'bool':
            return value_str.lower() in ('true', '1', 'yes', 'on')
        elif value_type == 'int':
            try:
                return int(value_str)
            except ValueError:
                return 0
        elif value_type == 'float':
            try:
                return float(value_str)
            except ValueError:
                return 0.0
        elif value_type == 'json':
            try:
                return json.loads(value_str)
            except (json.JSONDecodeError, TypeError):
                return {}
        else:  # string
            return value_str


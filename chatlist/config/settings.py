"""
Configuration management for ChatList application.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class Config:
    """Application configuration manager."""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Application paths
        self.project_root = Path(__file__).parent.parent.parent
        self.database_path = self.project_root / os.getenv('DATABASE_PATH', 'chatlist.db')
        self.env_file = self.project_root / '.env'

        # API Keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

        # Application settings
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_concurrent_requests = int(os.getenv('MAX_CONCURRENT_REQUESTS', '5'))
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))

        # UI settings
        self.ui_theme = os.getenv('UI_THEME', 'dark')
        self.window_width = int(os.getenv('WINDOW_WIDTH', '1200'))
        self.window_height = int(os.getenv('WINDOW_HEIGHT', '800'))

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup application logging."""
        log_level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }

        log_level = log_level_map.get(self.log_level.upper(), logging.INFO)

        # Create logs directory if it doesn't exist
        logs_dir = self.project_root / 'logs'
        logs_dir.mkdir(exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / 'chatlist.log'),
                logging.StreamHandler()
            ]
        )

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        key_map = {
            'openai': self.openai_api_key,
            'anthropic': self.anthropic_api_key,
            'google': self.google_api_key,
            'openrouter': self.openrouter_api_key,
        }
        return key_map.get(provider.lower())

    def is_api_key_set(self, provider: str) -> bool:
        """Check if API key is set for a provider."""
        return bool(self.get_api_key(provider))

    def get_database_url(self) -> str:
        """Get database connection URL."""
        return f"sqlite:///{self.database_path}"

    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings as dictionary."""
        return {
            'database_path': str(self.database_path),
            'log_level': self.log_level,
            'max_concurrent_requests': self.max_concurrent_requests,
            'request_timeout': self.request_timeout,
            'ui_theme': self.ui_theme,
            'window_width': self.window_width,
            'window_height': self.window_height,
            'api_keys': {
                'openai': bool(self.openai_api_key),
                'anthropic': bool(self.anthropic_api_key),
                'google': bool(self.google_api_key),
                'openrouter': bool(self.openrouter_api_key),
            }
        }


# Global config instance
config = Config()
"""
Database initialization script.
Run this to set up the database with initial schema and default models.
"""
import logging
from chatlist.db.database_manager import db_manager
from chatlist.db.model_manager import ModelManager
from chatlist.config.settings import config

logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database with schema and default models."""
    logger.info("Initializing database...")

    # Run migrations
    db_manager.initialize_database()

    # Add default models if they don't exist
    default_models = [
        {
            'name': 'OpenAI GPT-4',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key_var': 'OPENAI_API_KEY',
            'is_active': config.is_api_key_set('openai')
        },
        {
            'name': 'OpenAI GPT-3.5',
            'api_url': 'https://api.openai.com/v1/chat/completions',
            'api_key_var': 'OPENAI_API_KEY',
            'is_active': config.is_api_key_set('openai')
        },
        {
            'name': 'Anthropic Claude 3',
            'api_url': 'https://api.anthropic.com/v1/messages',
            'api_key_var': 'ANTHROPIC_API_KEY',
            'is_active': config.is_api_key_set('anthropic')
        },
        {
            'name': 'Google Gemini',
            'api_url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
            'api_key_var': 'GOOGLE_API_KEY',
            'is_active': config.is_api_key_set('google')
        },
    ]

    for model_data in default_models:
        existing = ModelManager.get_by_name(model_data['name'])
        if not existing:
            ModelManager.create(**model_data)
            logger.info(f"Added default model: {model_data['name']}")
        else:
            logger.debug(f"Model {model_data['name']} already exists")

    logger.info("Database initialization complete")


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    initialize_database()


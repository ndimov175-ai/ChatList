"""
Main application entry point for ChatList.
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication

from chatlist.config.settings import config
from chatlist.db.database_manager import db_manager
from chatlist.db.init_db import initialize_database
from chatlist.ui.main_window import MainWindow

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    # Initialize database
    try:
        initialize_database()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        print(f"Error initializing database: {e}")
        return 1

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ChatList")
    app.setOrganizationName("ChatList")

    # Create and show main window
    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        logger.error(f"Error creating main window: {e}")
        print(f"Error creating main window: {e}")
        return 1

    # Run application
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())


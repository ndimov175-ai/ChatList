"""Theme manager: safely apply UI themes at runtime."""
import logging
from typing import Optional

from PyQt6.QtWidgets import QApplication

logger = logging.getLogger(__name__)


def apply_theme(theme: Optional[str] = None) -> bool:
    """Apply a UI theme safely.

    Args:
        theme: 'dark' or 'light' (case-insensitive). If None, do nothing.

    Returns:
        True on success, False on failure.
    """
    if not theme:
        return False

    theme = str(theme).lower()

    try:
        app = QApplication.instance()
        if app is None:
            # No QApplication running (headless context) — nothing to apply
            logger.debug("No QApplication instance found when applying theme")
            return True

        # Keep styling simple and defensive to avoid crashes.
        if theme == 'dark':
            dark_qss = """
            QWidget { background-color: #232629; color: #dcdcdc; }
            QLineEdit, QTextEdit { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { background-color: #3a3a3a; color: #ffffff; }
            """
            app.setStyleSheet(dark_qss)
        elif theme == 'light':
            app.setStyleSheet("")
        else:
            # Unknown theme — no-op
            logger.debug(f"Unknown theme '{theme}' requested; no changes applied")

        logger.info(f"Applied theme: {theme}")
        return True
    except Exception as e:
        logger.error(f"Failed to apply theme '{theme}': {e}")
        try:
            # Attempt to clear stylesheet as fallback
            app = QApplication.instance()
            if app is not None:
                app.setStyleSheet("")
        except Exception:
            pass
        return False

"""
Settings dialog for application - allows choosing theme and panel width.
"""
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from chatlist.db.settings_manager import SettingsManager
from chatlist.config.settings import config
from chatlist.ui.theme_manager import apply_theme

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog to view and change application settings."""

    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(400)

        self.parent = parent

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
"""
Settings dialog: allows choosing UI theme and left-panel width.
Persists values using SettingsManager and applies splitter sizes.
"""
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt

from chatlist.db.settings_manager import SettingsManager
from chatlist.config.settings import config

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog to view and change a small set of application settings."""

    def __init__(self, parent: Optional[object] = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(420)

        self.parent = parent

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Theme selection
        theme_label = QLabel("UI Theme:")
        layout.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark", "dark")
        self.theme_combo.addItem("Light", "light")
        layout.addWidget(self.theme_combo)

        # Panel width (left) in pixels
        width_label = QLabel("Left panel width (px):")
        layout.addWidget(width_label)

        self.left_width_spin = QSpinBox()
        self.left_width_spin.setRange(200, 1600)
        self.left_width_spin.setSingleStep(50)
        layout.addWidget(self.left_width_spin)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def load_settings(self):
        # Load theme from settings table, fallback to config
        try:
            theme = SettingsManager.get('ui_theme', default=config.ui_theme)
        except Exception:
            theme = config.ui_theme

        if theme == 'light':
            self.theme_combo.setCurrentIndex(1)
        else:
            self.theme_combo.setCurrentIndex(0)

        # Load left panel width; default to 400 if not set
        try:
            left_width = SettingsManager.get('left_panel_width', default=400)
            self.left_width_spin.setValue(int(left_width))
        except Exception:
            self.left_width_spin.setValue(400)

    def on_save(self):
        # Persist settings
        # Ensure theme is a string value; prefer stored userData but fall back to text
        theme = self.theme_combo.currentData()
        if theme is None:
            theme = str(self.theme_combo.currentText()).lower()
        else:
            theme = str(theme)

        left_width = int(self.left_width_spin.value())

        ok1 = False
        ok2 = False
        try:
            ok1 = SettingsManager.set('ui_theme', theme, setting_type='string')
        except Exception as e:
            logger.error(f"Failed to save ui_theme: {e}")

        try:
            ok2 = SettingsManager.set('left_panel_width', left_width, setting_type='int')
        except Exception as e:
            logger.error(f"Failed to save left_panel_width: {e}")

        if ok1 and ok2:
            # Update runtime config
            config.ui_theme = theme

            # Apply splitter change immediately if possible
            try:
                if self.parent and hasattr(self.parent, 'splitter'):
                    sizes = self.parent.splitter.sizes()
                    total = sum(sizes) if sizes else (left_width * 2)
                    right = max(total - left_width, 200)
                    self.parent.splitter.setSizes([left_width, right])
            except Exception as e:
                logger.error(f"Failed to apply splitter sizes: {e}")

            # Apply theme (defensive)
            try:
                apply_theme(theme)
            except Exception as e:
                logger.error(f"apply_theme raised unexpectedly: {e}")

            QMessageBox.information(self, "Settings", "Settings saved")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings")
        app_layout.addRow("Log Level:", self.log_level_combo)



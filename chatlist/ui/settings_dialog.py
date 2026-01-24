"""
Settings dialog for application configuration.
"""
import logging
import json
from typing import Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QComboBox, QPushButton,
    QDialogButtonBox, QGroupBox, QLabel, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt

from chatlist.config.settings import config
from chatlist.db.settings_manager import SettingsManager

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """Dialog for application settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumSize(500, 400)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Application settings group
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        app_layout.addRow("Log Level:", self.log_level_combo)

        self.max_concurrent_spin = QSpinBox()
        self.max_concurrent_spin.setMinimum(1)
        self.max_concurrent_spin.setMaximum(20)
        app_layout.addRow("Max Concurrent Requests:", self.max_concurrent_spin)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(5)
        self.timeout_spin.setMaximum(300)
        self.timeout_spin.setSuffix(" seconds")
        app_layout.addRow("Request Timeout:", self.timeout_spin)

        layout.addWidget(app_group)

        # UI settings group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout(ui_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "system"])
        ui_layout.addRow("Theme:", self.theme_combo)

        self.width_spin = QSpinBox()
        self.width_spin.setMinimum(800)
        self.width_spin.setMaximum(3840)
        ui_layout.addRow("Window Width:", self.width_spin)

        self.height_spin = QSpinBox()
        self.height_spin.setMinimum(600)
        self.height_spin.setMaximum(2160)
        ui_layout.addRow("Window Height:", self.height_spin)

        layout.addWidget(ui_group)

        # Import/Export group
        import_export_group = QGroupBox("Import/Export Settings")
        import_export_layout = QVBoxLayout(import_export_group)

        buttons_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Settings")
        self.export_btn.clicked.connect(self.on_export_settings)
        buttons_layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("Import Settings")
        self.import_btn.clicked.connect(self.on_import_settings)
        buttons_layout.addWidget(self.import_btn)

        import_export_layout.addLayout(buttons_layout)
        layout.addWidget(import_export_group)

        # Note about API keys
        note_label = QLabel(
            "Note: API keys are stored in .env file and cannot be changed here."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note_label)

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )
        buttons.accepted.connect(self.on_save)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(
            self.on_restore_defaults
        )
        layout.addWidget(buttons)

    def load_settings(self):
        """Load current settings."""
        # Load from database settings or use config defaults
        log_level = SettingsManager.get('log_level', config.log_level)
        max_concurrent = SettingsManager.get('max_concurrent_requests', config.max_concurrent_requests)
        timeout = SettingsManager.get('request_timeout', config.request_timeout)
        theme = SettingsManager.get('ui_theme', config.ui_theme)
        width = SettingsManager.get('window_width', config.window_width)
        height = SettingsManager.get('window_height', config.window_height)

        # Set UI values
        index = self.log_level_combo.findText(log_level.upper())
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)

        self.max_concurrent_spin.setValue(max_concurrent)
        self.timeout_spin.setValue(timeout)

        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        else:
            self.theme_combo.setCurrentIndex(0)

        self.width_spin.setValue(width)
        self.height_spin.setValue(height)

    def on_save(self):
        """Save settings."""
        try:
            SettingsManager.set('log_level', self.log_level_combo.currentText().lower())
            SettingsManager.set('max_concurrent_requests', self.max_concurrent_spin.value(), 'int')
            SettingsManager.set('request_timeout', self.timeout_spin.value(), 'int')
            SettingsManager.set('ui_theme', self.theme_combo.currentText())
            SettingsManager.set('window_width', self.width_spin.value(), 'int')
            SettingsManager.set('window_height', self.height_spin.value(), 'int')

            QMessageBox.information(self, "Settings", "Settings saved successfully.")
            self.accept()
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def on_restore_defaults(self):
        """Restore default settings."""
        self.log_level_combo.setCurrentText("INFO")
        self.max_concurrent_spin.setValue(5)
        self.timeout_spin.setValue(30)
        self.theme_combo.setCurrentText("dark")
        self.width_spin.setValue(1200)
        self.height_spin.setValue(800)

    def on_export_settings(self):
        """Export settings to JSON file."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Export Settings",
                "chatlist_settings.json",
                "JSON Files (*.json)"
            )
            if not filename:
                return

            settings = {
                'log_level': self.log_level_combo.currentText().lower(),
                'max_concurrent_requests': self.max_concurrent_spin.value(),
                'request_timeout': self.timeout_spin.value(),
                'ui_theme': self.theme_combo.currentText(),
                'window_width': self.width_spin.value(),
                'window_height': self.height_spin.value()
            }

            with open(filename, 'w') as f:
                json.dump(settings, f, indent=2)

            QMessageBox.information(self, "Export", f"Settings exported to {filename}")
        except Exception as e:
            logger.error(f"Error exporting settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export settings: {e}")

    def on_import_settings(self):
        """Import settings from JSON file."""
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Import Settings",
                "",
                "JSON Files (*.json)"
            )
            if not filename:
                return

            with open(filename, 'r') as f:
                settings = json.load(f)

            # Update UI
            if 'log_level' in settings:
                index = self.log_level_combo.findText(settings['log_level'].upper())
                if index >= 0:
                    self.log_level_combo.setCurrentIndex(index)

            if 'max_concurrent_requests' in settings:
                self.max_concurrent_spin.setValue(settings['max_concurrent_requests'])

            if 'request_timeout' in settings:
                self.timeout_spin.setValue(settings['request_timeout'])

            if 'ui_theme' in settings:
                index = self.theme_combo.findText(settings['ui_theme'])
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)

            if 'window_width' in settings:
                self.width_spin.setValue(settings['window_width'])

            if 'window_height' in settings:
                self.height_spin.setValue(settings['window_height'])

            QMessageBox.information(self, "Import", "Settings imported successfully.")
        except Exception as e:
            logger.error(f"Error importing settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to import settings: {e}")


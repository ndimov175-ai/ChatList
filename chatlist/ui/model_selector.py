"""
Model selector widget with checkboxes.
"""
import logging
from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCheckBox, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

from chatlist.db.model_manager import ModelManager
from chatlist.config.settings import config

logger = logging.getLogger(__name__)


class ModelSelectorWidget(QWidget):
    """Widget for selecting models."""

    def __init__(self):
        super().__init__()
        self.model_checkboxes: dict = {}  # model_id -> QCheckBox
        self.init_ui()
        self.load_models()

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title = QLabel("Models")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Scroll area for model list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Container widget for checkboxes
        self.models_container = QWidget()
        self.models_layout = QVBoxLayout(self.models_container)
        self.models_layout.setContentsMargins(5, 5, 5, 5)
        self.models_layout.setSpacing(5)
        self.models_layout.addStretch()

        scroll.setWidget(self.models_container)
        layout.addWidget(scroll)

        # Select all / Deselect all buttons
        buttons_layout = QVBoxLayout()
        self.select_all_btn = QCheckBox("Select All")
        self.select_all_btn.stateChanged.connect(self.on_select_all_changed)
        buttons_layout.addWidget(self.select_all_btn)
        layout.addLayout(buttons_layout)

    def load_models(self):
        """Load models from database."""
        try:
            models = ModelManager.get_all()
            self.model_checkboxes.clear()

            # Clear existing checkboxes (except Select All)
            for i in reversed(range(self.models_layout.count())):
                item = self.models_layout.itemAt(i)
                if item.widget() and item.widget() != self.select_all_btn:
                    item.widget().deleteLater()

            # Add model checkboxes
            for model in models:
                checkbox = self._create_model_checkbox(model)
                self.model_checkboxes[model['id']] = checkbox
                # Insert before stretch
                self.models_layout.insertWidget(
                    self.models_layout.count() - 1,
                    checkbox
                )
        except Exception as e:
            logger.error(f"Error loading models: {e}")

    def _create_model_checkbox(self, model: dict) -> QCheckBox:
        """Create a checkbox for a model."""
        checkbox = QCheckBox(model['name'])
        checkbox.setChecked(model.get('is_active', False))

        # Check if API key is available
        api_key_var = model.get('api_key_var', '')
        has_api_key = config.is_api_key_set(
            api_key_var.lower().replace('_api_key', '')
        )

        # Set tooltip with status
        status = "API key available" if has_api_key else "API key missing"
        checkbox.setToolTip(
            f"Model: {model['name']}\n"
            f"API URL: {model.get('api_url', 'N/A')}\n"
            f"Status: {status}"
        )

        # Disable if no API key
        if not has_api_key:
            checkbox.setEnabled(False)
            checkbox.setStyleSheet("color: gray;")

        return checkbox

    def on_select_all_changed(self, state: int):
        """Handle select all checkbox state change."""
        checked = state == Qt.CheckState.Checked.value
        for checkbox in self.model_checkboxes.values():
            if checkbox.isEnabled():
                checkbox.setChecked(checked)

    def get_selected_model_ids(self) -> List[int]:
        """Get list of selected model IDs."""
        return [
            model_id
            for model_id, checkbox in self.model_checkboxes.items()
            if checkbox.isChecked() and checkbox.isEnabled()
        ]

    def get_selected_models(self) -> List[dict]:
        """Get list of selected model data."""
        selected_ids = self.get_selected_model_ids()
        return [
            ModelManager.get_by_id(model_id)
            for model_id in selected_ids
        ]


"""
Model management dialog for adding, editing, and deleting models.
"""
import logging
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QCheckBox, QPushButton, QDialogButtonBox,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from chatlist.db.model_manager import ModelManager
from chatlist.config.settings import config

logger = logging.getLogger(__name__)


class ModelEditDialog(QDialog):
    """Dialog for adding/editing a model."""

    def __init__(self, model_data: Optional[Dict[str, Any]] = None, parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.setWindowTitle("Edit Model" if model_data else "Add Model")
        self.setMinimumSize(500, 300)
        self.init_ui()

        if model_data:
            self.load_model_data(model_data)

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., GPT-4, Claude 3, Gemini Pro")
        form_layout.addRow("Model Name:", self.name_edit)

        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("e.g., https://api.openai.com/v1/chat/completions")
        form_layout.addRow("API URL:", self.api_url_edit)

        self.api_key_var_edit = QLineEdit()
        self.api_key_var_edit.setPlaceholderText("e.g., OPENAI_API_KEY")
        form_layout.addRow("API Key Variable:", self.api_key_var_edit)

        self.is_active_checkbox = QCheckBox("Active")
        self.is_active_checkbox.setChecked(True)
        form_layout.addRow("", self.is_active_checkbox)

        layout.addLayout(form_layout)

        # Info label
        info_label = QLabel(
            "Note: The API key variable should match the name in your .env file.\n"
            "The model will be disabled if the API key is not found."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_model_data(self, model_data: Dict[str, Any]):
        """Load model data into form."""
        self.name_edit.setText(model_data.get('name', ''))
        self.api_url_edit.setText(model_data.get('api_url', ''))
        self.api_key_var_edit.setText(model_data.get('api_key_var', ''))
        self.is_active_checkbox.setChecked(model_data.get('is_active', True))

    def validate_and_accept(self):
        """Validate form and accept."""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation", "Model name is required.")
            return

        if not self.api_url_edit.text().strip():
            QMessageBox.warning(self, "Validation", "API URL is required.")
            return

        if not self.api_key_var_edit.text().strip():
            QMessageBox.warning(self, "Validation", "API key variable is required.")
            return

        self.accept()

    def get_model_data(self) -> Dict[str, Any]:
        """Get model data from form."""
        return {
            'name': self.name_edit.text().strip(),
            'api_url': self.api_url_edit.text().strip(),
            'api_key_var': self.api_key_var_edit.text().strip(),
            'is_active': self.is_active_checkbox.isChecked()
        }


class ModelManagementDialog(QDialog):
    """Dialog for managing models."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Models")
        self.setMinimumSize(700, 500)
        self.init_ui()
        self.load_models()

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name", "API URL", "API Key Var", "Active", "API Key Status"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.add_btn = QPushButton("Add Model")
        self.add_btn.clicked.connect(self.on_add_model)
        buttons_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self.on_edit_model)
        self.edit_btn.setEnabled(False)
        buttons_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.on_delete_model)
        self.delete_btn.setEnabled(False)
        buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addStretch()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_models)
        buttons_layout.addWidget(self.refresh_btn)

        layout.addLayout(buttons_layout)

        # Connect selection changes
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        # Dialog buttons
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        dialog_buttons.rejected.connect(self.accept)
        layout.addWidget(dialog_buttons)

    def load_models(self):
        """Load models into table."""
        try:
            models = ModelManager.get_all()
            self.table.setRowCount(len(models))

            for row, model in enumerate(models):
                # Name
                name_item = QTableWidgetItem(model['name'])
                self.table.setItem(row, 0, name_item)

                # API URL
                url_item = QTableWidgetItem(model.get('api_url', ''))
                self.table.setItem(row, 1, url_item)

                # API Key Variable
                key_var_item = QTableWidgetItem(model.get('api_key_var', ''))
                self.table.setItem(row, 2, key_var_item)

                # Active
                active_item = QTableWidgetItem("Yes" if model.get('is_active') else "No")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, active_item)

                # API Key Status
                api_key_var = model.get('api_key_var', '')
                has_key = config.is_api_key_set(
                    api_key_var.lower().replace('_api_key', '')
                )
                status_item = QTableWidgetItem("Available" if has_key else "Missing")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if not has_key:
                    status_item.setForeground(QColor(200, 0, 0))  # Red
                self.table.setItem(row, 4, status_item)

                # Store model ID in item data
                name_item.setData(Qt.ItemDataRole.UserRole, model['id'])

            self.table.resizeRowsToContents()
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load models: {e}")

    def on_selection_changed(self):
        """Handle table selection changes."""
        has_selection = len(self.table.selectedIndexes()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def get_selected_model_id(self) -> Optional[int]:
        """Get selected model ID."""
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        if not selected_rows:
            return None

        row = next(iter(selected_rows))
        item = self.table.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def on_add_model(self):
        """Add a new model."""
        dialog = ModelEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                model_data = dialog.get_model_data()
                ModelManager.create(**model_data)
                self.load_models()
                QMessageBox.information(self, "Success", "Model added successfully.")
            except Exception as e:
                logger.error(f"Error adding model: {e}")
                QMessageBox.critical(self, "Error", f"Failed to add model: {e}")

    def on_edit_model(self):
        """Edit selected model."""
        model_id = self.get_selected_model_id()
        if not model_id:
            return

        try:
            model_data = ModelManager.get_by_id(model_id)
            if not model_data:
                QMessageBox.warning(self, "Error", "Model not found.")
                return

            dialog = ModelEditDialog(model_data, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_model_data()
                ModelManager.update(model_id, **new_data)
                self.load_models()
                QMessageBox.information(self, "Success", "Model updated successfully.")
        except Exception as e:
            logger.error(f"Error editing model: {e}")
            QMessageBox.critical(self, "Error", f"Failed to edit model: {e}")

    def on_delete_model(self):
        """Delete selected model."""
        model_id = self.get_selected_model_id()
        if not model_id:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this model?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                ModelManager.delete(model_id)
                self.load_models()
                QMessageBox.information(self, "Success", "Model deleted successfully.")
            except Exception as e:
                logger.error(f"Error deleting model: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete model: {e}")


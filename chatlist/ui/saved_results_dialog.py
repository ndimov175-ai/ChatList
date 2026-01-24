"""
Saved results dialog for viewing stored prompt responses from the database.
"""
import logging
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QLabel, QPushButton, QSplitter, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt

from chatlist.db.result_manager import ResultManager

logger = logging.getLogger(__name__)


class SavedResultsDialog(QDialog):
    """Dialog for viewing saved results from the database."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results: List[Dict[str, Any]] = []
        self.init_ui()
        self.load_results()

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Saved Results")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Saved Prompt Responses")
        title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(title)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left panel - Results list
        left_widget = QFrame()
        left_widget.setFrameStyle(QFrame.Shape.Box)
        left_layout = QVBoxLayout(left_widget)

        list_label = QLabel("Saved Results:")
        list_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(list_label)

        self.results_list = QListWidget()
        self.results_list.itemSelectionChanged.connect(self.on_result_selected)
        left_layout.addWidget(self.results_list)

        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_results)
        left_layout.addWidget(refresh_btn)

        splitter.addWidget(left_widget)

        # Right panel - Result details
        right_widget = QFrame()
        right_widget.setFrameStyle(QFrame.Shape.Box)
        right_layout = QVBoxLayout(right_widget)

        details_label = QLabel("Result Details:")
        details_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(details_label)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        right_layout.addWidget(self.details_text)

        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([300, 700])

        # Bottom buttons
        buttons_layout = QHBoxLayout()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)

        layout.addLayout(buttons_layout)

    def load_results(self):
        """Load saved results from database."""
        try:
            self.results = ResultManager.get_all(limit=100)  # Limit to last 100 results
            self.results_list.clear()

            for result in self.results:
                # Create display text
                model_name = result.get('model_name', 'Unknown Model')
                prompt_preview = result.get('prompt_text', '')[:50]
                if len(prompt_preview) == 50:
                    prompt_preview += "..."
                saved_at = result.get('saved_at', '')

                display_text = f"{model_name} - {prompt_preview}"
                if saved_at:
                    display_text += f" ({saved_at[:19]})"  # Show date/time

                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, result)
                self.results_list.addItem(item)

            logger.info(f"Loaded {len(self.results)} saved results")

        except Exception as e:
            logger.error(f"Failed to load saved results: {e}")
            QMessageBox.warning(self, "Error", f"Failed to load saved results: {e}")

    def on_result_selected(self):
        """Handle result selection in the list."""
        current_item = self.results_list.currentItem()
        if not current_item:
            return

        result = current_item.data(Qt.ItemDataRole.UserRole)
        if not result:
            return

        # Format the result details
        details = f"""Model: {result.get('model_name', 'Unknown')}
Prompt: {result.get('prompt_text', '')}
Response Time: {result.get('response_time', 'N/A')} seconds
Tokens Used: {result.get('tokens_used', 'N/A')}
Saved At: {result.get('saved_at', 'N/A')}

Response:
{result.get('response_text', '')}
"""

        self.details_text.setPlainText(details)
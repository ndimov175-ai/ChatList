"""
Prompt input widget with saved prompts selection.
"""
import logging
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QComboBox, QLabel, QLineEdit, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import pyqtSignal, Qt

from chatlist.db.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class PromptInputWidget(QWidget):
    """Widget for inputting and managing prompts."""

    send_request = pyqtSignal(str)
    save_prompt = pyqtSignal(str, list)  # prompt_text, tags

    def __init__(self):
        super().__init__()
        self.current_prompt_id: Optional[int] = None
        self.init_ui()
        self.load_saved_prompts()

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title = QLabel("Prompt")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Saved prompts selector
        saved_layout = QHBoxLayout()
        saved_layout.addWidget(QLabel("Saved Prompts:"))
        self.saved_prompts_combo = QComboBox()
        self.saved_prompts_combo.addItem("-- New Prompt --", None)
        self.saved_prompts_combo.currentIndexChanged.connect(self.on_prompt_selected)
        saved_layout.addWidget(self.saved_prompts_combo)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.on_load_prompt)
        saved_layout.addWidget(load_btn)

        layout.addLayout(saved_layout)

        # Prompt text area
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText("Enter your prompt here...")
        self.prompt_text.setMinimumHeight(150)
        layout.addWidget(self.prompt_text)

        # Tags input
        tags_layout = QHBoxLayout()
        tags_layout.addWidget(QLabel("Tags:"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("tag1, tag2, tag3")
        tags_layout.addWidget(self.tags_input)
        layout.addLayout(tags_layout)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("Save Prompt")
        self.save_btn.clicked.connect(self.on_save_prompt)
        buttons_layout.addWidget(self.save_btn)

        buttons_layout.addStretch()

        self.send_btn = QPushButton("Send Request")
        self.send_btn.setStyleSheet("font-weight: bold;")
        self.send_btn.clicked.connect(self.on_send_request)
        buttons_layout.addWidget(self.send_btn)

        layout.addLayout(buttons_layout)

    def load_saved_prompts(self):
        """Load saved prompts into combo box."""
        try:
            prompts = PromptManager.get_all(limit=50)
            self.saved_prompts_combo.clear()
            self.saved_prompts_combo.addItem("-- New Prompt --", None)

            for prompt in prompts:
                text = prompt['prompt_text']
                preview = text[:50] + "..." if len(text) > 50 else text
                display_text = f"{preview} ({prompt['date_created'][:10]})"
                self.saved_prompts_combo.addItem(display_text, prompt['id'])
        except Exception as e:
            logger.error(f"Error loading saved prompts: {e}")

    def on_prompt_selected(self, index: int):
        """Handle prompt selection from combo box."""
        # Don't auto-load, user must click Load button
        pass

    def on_load_prompt(self):
        """Load selected prompt."""
        prompt_id = self.saved_prompts_combo.currentData()
        if not prompt_id:
            return

        try:
            prompt = PromptManager.get_by_id(prompt_id)
            if prompt:
                self.prompt_text.setPlainText(prompt['prompt_text'])
                tags = prompt.get('tags', [])
                self.tags_input.setText(", ".join(tags))
                self.current_prompt_id = prompt_id
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")

    def on_save_prompt(self):
        """Save current prompt."""
        prompt_text = self.prompt_text.toPlainText().strip()
        if not prompt_text:
            return

        # Parse tags
        tags_str = self.tags_input.text().strip()
        tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]

        self.save_prompt.emit(prompt_text, tags)

    def on_send_request(self):
        """Send request signal."""
        prompt_text = self.prompt_text.toPlainText().strip()
        if prompt_text:
            self.send_request.emit(prompt_text)

    def get_prompt_text(self) -> str:
        """Get current prompt text."""
        return self.prompt_text.toPlainText()

    def clear(self):
        """Clear prompt input."""
        self.prompt_text.clear()
        self.tags_input.clear()
        self.saved_prompts_combo.setCurrentIndex(0)
        self.current_prompt_id = None


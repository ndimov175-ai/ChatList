"""
Result comparison widget for side-by-side comparison of responses.
"""
import logging
from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel,
    QSplitter, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt

from chatlist.core.request_processor import RequestResult

logger = logging.getLogger(__name__)


class ResultComparisonWidget(QWidget):
    """Widget for comparing multiple results side-by-side."""

    def __init__(self):
        super().__init__()
        self.results: List[RequestResult] = []
        self.init_ui()

    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Title
        title = QLabel("Response Comparison")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Scroll area for comparison panels
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Container for comparison panels
        self.comparison_container = QWidget()
        self.comparison_layout = QHBoxLayout(self.comparison_container)
        self.comparison_layout.setContentsMargins(5, 5, 5, 5)
        self.comparison_layout.setSpacing(5)

        scroll.setWidget(self.comparison_container)
        layout.addWidget(scroll)

    def display_results(self, results: List[RequestResult]):
        """Display results for comparison."""
        self.results = results

        # Clear existing panels
        for i in reversed(range(self.comparison_layout.count())):
            item = self.comparison_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        if not results:
            return

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.comparison_layout.addWidget(splitter)

        # Create a panel for each result
        for result in results:
            panel = self._create_result_panel(result)
            splitter.addWidget(panel)

        # Set equal sizes
        if splitter.count() > 0:
            splitter.setSizes([1] * splitter.count())

    def _create_result_panel(self, result: RequestResult) -> QWidget:
        """Create a panel for a single result."""
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(5, 5, 5, 5)
        panel_layout.setSpacing(5)

        # Header with model name and stats
        header = QLabel()
        header.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f0f0f0;")
        
        stats_parts = [result.model_name]
        if result.response.response_time:
            stats_parts.append(f"Time: {result.response.response_time:.2f}s")
        if result.response.tokens_used:
            stats_parts.append(f"Tokens: {result.response.tokens_used}")
        
        header.setText(" | ".join(stats_parts))
        panel_layout.addWidget(header)

        # Response text
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        if result.response.error:
            text_edit.setPlainText(f"Error: {result.response.error}")
            text_edit.setStyleSheet("background-color: #ffe0e0;")
        else:
            text_edit.setPlainText(result.response.text)
            if result.success:
                text_edit.setStyleSheet("background-color: #e0ffe0;")
            else:
                text_edit.setStyleSheet("background-color: #fff0e0;")

        panel_layout.addWidget(text_edit)

        return panel

    def clear(self):
        """Clear comparison view."""
        self.results.clear()
        for i in reversed(range(self.comparison_layout.count())):
            item = self.comparison_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()


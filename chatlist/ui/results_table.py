"""
Results table widget for displaying model responses.
"""
import logging
from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QHBoxLayout, QLabel, QTextEdit,
    QDialog, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from chatlist.core.request_processor import RequestResult
from chatlist.ui.markdown_viewer import MarkdownViewerDialog

logger = logging.getLogger(__name__)


class ResultDetailDialog(QDialog):
    """Dialog for viewing full result details."""

    def __init__(self, result_data: dict, parent=None):
        super().__init__(parent)
        self.result_data = result_data
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI."""
        self.setWindowTitle(f"Result: {self.result_data.get('model_name', 'Unknown')}")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Model info
        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel(f"Model: {self.result_data.get('model_name', 'Unknown')}"))
        if self.result_data.get('response_time'):
            info_layout.addWidget(QLabel(f"Time: {self.result_data['response_time']:.2f}s"))
        if self.result_data.get('tokens_used'):
            info_layout.addWidget(QLabel(f"Tokens: {self.result_data['tokens_used']}"))
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Response text
        layout.addWidget(QLabel("Response:"))
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(self.result_data.get('response_text', ''))
        layout.addWidget(text_edit)

        # Error if present
        if self.result_data.get('error'):
            error_label = QLabel(f"Error: {self.result_data['error']}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        copy_btn = buttons.addButton("Copy", QDialogButtonBox.ButtonRole.ActionRole)
        copy_btn.clicked.connect(
            lambda: self.copy_to_clipboard(text_edit.toPlainText())
        )
        layout.addWidget(buttons)

    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Copied", "Response copied to clipboard")


class ResultsTableWidget(QWidget):
    """Widget for displaying results in a table."""

    save_result = pyqtSignal(dict)  # result_data

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
        title = QLabel("Results")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Model", "Response", "Time (s)", "Tokens"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setWordWrap(True)  # Enable word wrap for table cells
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        layout.addWidget(self.table)

        # Buttons
        buttons_layout = QHBoxLayout()

        self.view_btn = QPushButton("View Details")
        self.view_btn.clicked.connect(self.on_view_details)
        self.view_btn.setEnabled(False)
        buttons_layout.addWidget(self.view_btn)

        self.open_btn = QPushButton("Open")
        self.open_btn.clicked.connect(self.on_open_markdown)
        self.open_btn.setEnabled(False)
        buttons_layout.addWidget(self.open_btn)

        self.save_btn = QPushButton("Save Selected")
        self.save_btn.clicked.connect(self.on_save_selected)
        self.save_btn.setEnabled(False)
        buttons_layout.addWidget(self.save_btn)

        buttons_layout.addStretch()

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_results)
        buttons_layout.addWidget(self.clear_btn)

        layout.addLayout(buttons_layout)

        # Connect selection changes
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

    def display_results(self, results: List[RequestResult]):
        """Display results in the table."""
        self.results = results
        self.table.setRowCount(len(results))

        for row, result in enumerate(results):
            # Model name
            model_item = QTableWidgetItem(result.model_name)
            self.table.setItem(row, 0, model_item)

            # Response text (multi-line)
            response_text = result.response.text
            if result.response.error:
                response_text = f"Error: {result.response.error}"
                model_item.setForeground(QColor(200, 0, 0))  # Red for errors
            else:
                # Show more text (up to 500 chars, but allow multi-line)
                if len(response_text) > 500:
                    response_text = response_text[:500] + "..."
            
            # Create item with word wrap enabled
            response_item = QTableWidgetItem(response_text)
            response_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            # Enable word wrap for the item
            response_item.setFlags(response_item.flags() | Qt.ItemFlag.ItemIsEditable)
            response_item.setFlags(response_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Keep read-only but allow wrap
            self.table.setItem(row, 1, response_item)
            
            # Set row height to accommodate multiple lines
            # Calculate height based on text length and line breaks
            line_count = max(1, response_text.count('\n') + 1)
            # Estimate: ~20px per line, minimum 60px, max 200px for very long responses
            estimated_height = min(max(60, line_count * 20 + 20), 200)
            self.table.setRowHeight(row, estimated_height)

            # Response time
            time_text = f"{result.response.response_time:.2f}" if result.response.response_time else "N/A"
            time_item = QTableWidgetItem(time_text)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 2, time_item)

            # Tokens
            tokens_text = str(result.response.tokens_used) if result.response.tokens_used else "N/A"
            tokens_item = QTableWidgetItem(tokens_text)
            tokens_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 3, tokens_item)

            # Color code rows
            if result.success:
                for col in range(4):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(240, 255, 240))  # Light green
            else:
                for col in range(4):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(255, 240, 240))  # Light red

        # Ensure minimum row heights are maintained
        for row in range(self.table.rowCount()):
            current_height = self.table.rowHeight(row)
            if current_height < 60:
                self.table.setRowHeight(row, 60)

    def on_selection_changed(self):
        """Handle table selection changes."""
        has_selection = len(self.table.selectedIndexes()) > 0
        self.view_btn.setEnabled(has_selection)
        self.open_btn.setEnabled(has_selection)
        self.save_btn.setEnabled(has_selection)

    def on_cell_double_clicked(self, row: int, column: int):
        """Handle cell double-click."""
        if row < len(self.results):
            self.show_result_details(row)

    def on_view_details(self):
        """View details of selected result."""
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        if selected_rows:
            row = next(iter(selected_rows))
            self.show_result_details(row)

    def on_open_markdown(self):
        """Open selected result in markdown viewer."""
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        if not selected_rows:
            return
        
        row = next(iter(selected_rows))
        if row >= len(self.results):
            return
        
        result = self.results[row]
        if not result.success or result.response.error:
            return
        
        # Get response text
        markdown_text = result.response.text
        
        # Create and show markdown viewer dialog
        dialog = MarkdownViewerDialog(
            f"Response: {result.model_name}",
            markdown_text,
            self
        )
        dialog.exec()

    def show_result_details(self, row: int):
        """Show detailed view of a result."""
        if row >= len(self.results):
            return

        result = self.results[row]
        result_data = {
            'model_id': result.model_id,
            'model_name': result.model_name,
            'response_text': result.response.text,
            'response_time': result.response.response_time,
            'tokens_used': result.response.tokens_used,
            'error': result.response.error
        }

        dialog = ResultDetailDialog(result_data, self)
        dialog.exec()

    def on_save_selected(self):
        """Save selected results to database."""
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        if not selected_rows:
            return

        saved_count = 0
        for row in selected_rows:
            if row < len(self.results):
                result = self.results[row]
                if result.success:
                    result_data = {
                        'model_id': result.model_id,
                        'response_text': result.response.text,
                        'response_time': result.response.response_time,
                        'tokens_used': result.response.tokens_used
                    }
                    self.save_result.emit(result_data)
                    saved_count += 1

        if saved_count > 0:
            QMessageBox.information(
                self,
                "Saved",
                f"Saved {saved_count} result(s) to database."
            )

    def clear_results(self):
        """Clear all results."""
        self.results.clear()
        self.table.setRowCount(0)
        self.view_btn.setEnabled(False)
        self.open_btn.setEnabled(False)
        self.save_btn.setEnabled(False)


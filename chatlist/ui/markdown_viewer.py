"""
Markdown viewer dialog for displaying formatted responses.
"""
import logging
import re
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QDialogButtonBox, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCharFormat, QTextCursor, QTextDocument, QSyntaxHighlighter

logger = logging.getLogger(__name__)


class MarkdownHighlighter(QSyntaxHighlighter):
    """Simple markdown syntax highlighter for QTextEdit."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Headers
        header_format = QTextCharFormat()
        header_format.setFontWeight(700)
        header_format.setForeground(Qt.GlobalColor.darkBlue)
        self.highlighting_rules.append((r'^#{1,6}\s+(.+)$', header_format))
        
        # Bold
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(700)
        self.highlighting_rules.append((r'\*\*(.+?)\*\*', bold_format))
        self.highlighting_rules.append((r'__(.+?)__', bold_format))
        
        # Italic
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.highlighting_rules.append((r'\*(.+?)\*', italic_format))
        self.highlighting_rules.append((r'_(.+?)_', italic_format))
        
        # Code blocks
        code_format = QTextCharFormat()
        code_format.setFontFamily("monospace")
        code_format.setBackground(Qt.GlobalColor.lightGray)
        self.highlighting_rules.append((r'`(.+?)`', code_format))
        
        # Links
        link_format = QTextCharFormat()
        link_format.setForeground(Qt.GlobalColor.blue)
        link_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        self.highlighting_rules.append((r'\[([^\]]+)\]\(([^\)]+)\)', link_format))
    
    def highlightBlock(self, text):
        """Apply highlighting rules to text block."""
        for pattern, format in self.highlighting_rules:
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)


class MarkdownViewerDialog(QDialog):
    """Dialog for viewing markdown-formatted text."""
    
    def __init__(self, title: str, markdown_text: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(700, 500)
        self.markdown_text = markdown_text
        self.init_ui()
        self.load_markdown()
    
    def init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(self.windowTitle())
        title_label.setStyleSheet("font-weight: bold; font-size: 16px; padding: 5px;")
        layout.addWidget(title_label)
        
        # Text editor with markdown support
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontFamily("Arial")
        self.text_edit.setFontPointSize(10)
        
        # Add markdown highlighter
        self.highlighter = MarkdownHighlighter(self.text_edit.document())
        
        layout.addWidget(self.text_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Copy
        )
        buttons.accepted.connect(self.accept)
        copy_btn = buttons.button(QDialogButtonBox.StandardButton.Copy)
        copy_btn.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(buttons)
    
    def load_markdown(self):
        """Load and display markdown text."""
        # Convert markdown to HTML for better rendering
        html = self.markdown_to_html(self.markdown_text)
        self.text_edit.setHtml(html)
    
    def markdown_to_html(self, text: str) -> str:
        """Convert markdown to HTML."""
        html = text
        
        # Escape HTML special characters first
        html = html.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        
        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Code blocks (triple backticks)
        html = re.sub(
            r'```(\w+)?\n(.*?)```',
            r'<pre style="background-color: #f4f4f4; padding: 10px; border-radius: 5px;"><code>\2</code></pre>',
            html,
            flags=re.DOTALL
        )
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">\1</code>', html)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        html = '<p>' + html + '</p>'
        
        # Wrap in styled div
        html = f'''
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 10px;">
        {html}
        </div>
        '''
        
        return html
    
    def copy_to_clipboard(self):
        """Copy markdown text to clipboard."""
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.markdown_text)


"""
About dialog showing application information, license, and credits.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
from chatlist.config.settings import config


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About ChatList")
        self.setMinimumSize(500, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel(f"ChatList - AI Model Comparison Tool")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        version = QLabel(f"Version: 0.1.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        info = QTextEdit()
        info.setReadOnly(True)
        info.setPlainText(
            """
ChatList is a lightweight desktop application for comparing responses
from multiple AI models. It supports sending the same prompt to several
models and viewing results side-by-side.

License: MIT

Credits:
- Developed by the ChatList contributors

For more information, see the project documentation and repository.
"""
        )
        layout.addWidget(info)

        btn_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

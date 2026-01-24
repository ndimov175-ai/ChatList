"""
Main window for ChatList application.
"""
import logging
import asyncio
from typing import List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMenuBar,
    QToolBar, QStatusBar, QMessageBox, QSplitter, QProgressBar, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon

from chatlist.config.settings import config
from chatlist.ui.prompt_input import PromptInputWidget
from chatlist.ui.model_selector import ModelSelectorWidget
from chatlist.ui.results_table import ResultsTableWidget
from chatlist.core.request_processor import RequestProcessor, RequestResult

logger = logging.getLogger(__name__)


class RequestWorker(QThread):
    """Worker thread for async API requests."""
    progress = pyqtSignal(int, str)  # model_id, status_message
    finished = pyqtSignal(list)  # List[RequestResult]

    def __init__(self, processor: RequestProcessor, model_ids: List[int], prompt: str):
        super().__init__()
        self.processor = processor
        self.model_ids = model_ids
        self.prompt = prompt

    def run(self):
        """Run async request processing."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        def progress_callback(model_id: int, message: str):
            self.progress.emit(model_id, message)

        try:
            results = loop.run_until_complete(
                self.processor.send_to_models(
                    self.model_ids,
                    self.prompt,
                    progress_callback
                )
            )
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"Error in request worker: {e}")
            self.finished.emit([])
        finally:
            loop.close()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.request_processor = RequestProcessor()
        self.request_worker: Optional[RequestWorker] = None
        self.current_prompt_id: Optional[int] = None
        self.init_ui()
        self.init_menu()
        self.init_toolbar()
        self.init_statusbar()

    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("ChatList - AI Model Comparison Tool")
        self.setGeometry(100, 100, config.window_width, config.window_height)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Indeterminate mode
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel: Prompt input and model selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Prompt input widget
        self.prompt_input = PromptInputWidget()
        self.prompt_input.send_request.connect(self.on_send_request)
        self.prompt_input.save_prompt.connect(self.on_save_prompt)
        left_layout.addWidget(self.prompt_input)

        # Model selector widget
        self.model_selector = ModelSelectorWidget()
        left_layout.addWidget(self.model_selector)

        splitter.addWidget(left_panel)

        # Right panel: Results table
        self.results_table = ResultsTableWidget()
        self.results_table.save_result.connect(self.on_save_result)
        splitter.addWidget(self.results_table)

        # Set splitter proportions (40% left, 60% right)
        splitter.setSizes([400, 600])

    def init_menu(self):
        """Initialize menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.on_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def init_toolbar(self):
        """Initialize toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Send request action
        self.send_action = QAction("Send Request", self)
        self.send_action.setShortcut("Ctrl+Return")
        self.send_action.triggered.connect(self.on_send_request_clicked)
        toolbar.addAction(self.send_action)

        # Cancel action
        self.cancel_action = QAction("Cancel", self)
        self.cancel_action.setShortcut("Ctrl+C")
        self.cancel_action.triggered.connect(self.on_cancel_request)
        self.cancel_action.setEnabled(False)
        toolbar.addAction(self.cancel_action)

        toolbar.addSeparator()

        # Clear results action
        clear_action = QAction("Clear Results", self)
        clear_action.triggered.connect(self.results_table.clear_results)
        toolbar.addAction(clear_action)

    def init_statusbar(self):
        """Initialize status bar."""
        self.statusBar().showMessage("Ready")

    def on_new(self):
        """Handle New action."""
        self.prompt_input.clear()
        self.results_table.clear_results()
        self.current_prompt_id = None
        self.statusBar().showMessage("Cleared")

    def on_settings(self):
        """Handle Settings action."""
        from chatlist.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec()

    def on_manage_models(self):
        """Handle Manage Models action."""
        from chatlist.ui.model_dialog import ModelManagementDialog
        dialog = ModelManagementDialog(self)
        dialog.exec()
        # Refresh model selector after changes
        self.model_selector.load_models()

    def on_about(self):
        """Handle About action."""
        QMessageBox.about(
            self,
            "About ChatList",
            "ChatList - AI Model Comparison Tool\n\n"
            "Version 0.1.0\n\n"
            "Compare responses from multiple AI models simultaneously."
        )

    def on_send_request_clicked(self):
        """Handle send request from toolbar."""
        prompt_text = self.prompt_input.get_prompt_text()
        if not prompt_text.strip():
            QMessageBox.warning(self, "Warning", "Please enter a prompt.")
            return
        self.on_send_request(prompt_text)

    def on_send_request(self, prompt_text: str):
        """Handle send request signal."""
        if not prompt_text.strip():
            return

        # Get selected model IDs
        selected_model_ids = self.model_selector.get_selected_model_ids()
        if not selected_model_ids:
            QMessageBox.warning(self, "Warning", "Please select at least one model.")
            return

        # Clear previous results
        self.results_table.clear_results()

        # Update status
        self.statusBar().showMessage(f"Sending request to {len(selected_model_ids)} model(s)...")

        # Disable UI during request
        self.prompt_input.setEnabled(False)
        self.model_selector.setEnabled(False)
        self.send_action.setEnabled(False)
        self.cancel_action.setEnabled(True)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(0)  # Indeterminate mode

        # Create and start worker thread
        self.request_worker = RequestWorker(
            self.request_processor,
            selected_model_ids,
            prompt_text
        )
        self.request_worker.progress.connect(self.on_request_progress)
        self.request_worker.finished.connect(self.on_request_finished)
        self.request_worker.start()

    def on_request_progress(self, model_id: int, message: str):
        """Handle request progress update."""
        self.statusBar().showMessage(message)

    def on_request_finished(self, results: List[RequestResult]):
        """Handle request completion."""
        # Re-enable UI
        self.prompt_input.setEnabled(True)
        self.model_selector.setEnabled(True)
        self.send_action.setEnabled(True)
        self.cancel_action.setEnabled(False)
        
        # Hide progress bar
        self.progress_bar.setVisible(False)

        # Display results
        self.results_table.display_results(results)

        # Update status
        successful = sum(1 for r in results if r.success)
        total = len(results)
        self.statusBar().showMessage(
            f"Completed: {successful}/{total} successful"
        )

        # Cleanup worker
        if self.request_worker:
            self.request_worker.quit()
            self.request_worker.wait()
            self.request_worker = None

    def on_cancel_request(self):
        """Handle cancel request."""
        if self.request_processor:
            self.request_processor.cancel_requests()
        if self.request_worker and self.request_worker.isRunning():
            self.request_worker.terminate()
            self.request_worker.wait()
            self.request_worker = None
        
        # Re-enable UI
        self.prompt_input.setEnabled(True)
        self.model_selector.setEnabled(True)
        self.send_action.setEnabled(True)
        self.cancel_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Request cancelled")

    def on_save_prompt(self, prompt_text: str, tags: List[str]):
        """Handle save prompt signal."""
        from chatlist.db.prompt_manager import PromptManager

        try:
            if self.current_prompt_id:
                PromptManager.update(
                    self.current_prompt_id,
                    prompt_text=prompt_text,
                    tags=tags
                )
                self.statusBar().showMessage("Prompt updated")
            else:
                prompt_id = PromptManager.create(
                    prompt_text=prompt_text,
                    tags=tags
                )
                self.current_prompt_id = prompt_id
                self.statusBar().showMessage("Prompt saved")
        except Exception as e:
            logger.error(f"Error saving prompt: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save prompt: {e}")

    def on_save_result(self, result_data: dict):
        """Handle save result signal."""
        from chatlist.db.result_manager import ResultManager

        try:
            if not self.current_prompt_id:
                # Create prompt first
                from chatlist.db.prompt_manager import PromptManager
                prompt_text = self.prompt_input.get_prompt_text()
                self.current_prompt_id = PromptManager.create(prompt_text=prompt_text)

            ResultManager.create(
                prompt_id=self.current_prompt_id,
                model_id=result_data['model_id'],
                response_text=result_data['response_text'],
                response_time=result_data['response_time'],
                tokens_used=result_data.get('tokens_used')
            )
            self.statusBar().showMessage("Result saved")
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save result: {e}")

    def closeEvent(self, event):
        """Handle window close event."""
        # Cleanup request processor
        if self.request_processor:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.request_processor.cleanup())
                loop.close()
            except Exception as e:
                logger.error(f"Error cleaning up: {e}")

        # Wait for worker thread
        if self.request_worker and self.request_worker.isRunning():
            self.request_worker.terminate()
            self.request_worker.wait()

        event.accept()


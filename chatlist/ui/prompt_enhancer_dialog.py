"""
Dialog for prompt enhancement with UI for input, results, and alternatives.
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QComboBox,
    QPushButton, QLabel, QProgressBar, QTabWidget, QWidget,
    QMessageBox, QListWidget, QListWidgetItem, QSplitter, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from chatlist.core.prompt_enhancer_manager import PromptEnhancerManager
from chatlist.core.enhance_result import EnhanceResult
from chatlist.db.model_manager import ModelManager

logger = logging.getLogger(__name__)


class EnhancementWorker(QThread):
    """Worker thread for prompt enhancement."""
    finished = pyqtSignal(EnhanceResult)
    error = pyqtSignal(str)

    def __init__(self, manager: PromptEnhancerManager, prompt: str, model_id: int, enhancement_type: str):
        super().__init__()
        self.manager = manager
        self.prompt = prompt
        self.model_id = model_id
        self.enhancement_type = enhancement_type

    def run(self):
        """Run the enhancement in a separate thread."""
        try:
            result = self.manager.enhance_prompt(
                self.prompt,
                self.model_id,
                self.enhancement_type
            )
            if result:
                self.finished.emit(result)
            else:
                self.error.emit("Ошибка обработки ответа модели. Попробуйте другую модель.")
        except Exception as e:
            logger.error(f"Error in enhancement worker: {e}")
            self.error.emit(f"Ошибка: {str(e)}")


class PromptEnhancerDialog(QDialog):
    """Dialog for enhancing prompts with AI."""

    # Signal for passing selected prompt back to main window
    prompt_selected = pyqtSignal(str)

    def __init__(self, initial_prompt: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI-ассистент для улучшения промтов")
        self.setGeometry(100, 100, 1100, 700)
        self.setMinimumSize(900, 600)

        self.manager = PromptEnhancerManager()
        self.current_result: EnhanceResult = None
        self.worker: EnhancementWorker = None

        self.init_ui(initial_prompt)

    def init_ui(self, initial_prompt: str):
        """Initialize the user interface."""
        main_layout = QHBoxLayout(self)

        # Left panel: Input section
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Title
        title = QLabel("Исходный промт")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)
        title.setFont(title_font)
        left_layout.addWidget(title)

        # Prompt input
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlainText(initial_prompt)
        self.prompt_input.setMinimumHeight(150)
        left_layout.addWidget(self.prompt_input)

        # Enhancement type selector
        type_label = QLabel("Тип улучшения:")
        left_layout.addWidget(type_label)

        self.enhancement_type_combo = QComboBox()
        enhancement_types = [
            ("Общее улучшение", "general"),
            ("Для программирования", "code"),
            ("Для анализа", "analysis"),
            ("Для творчества", "creative")
        ]
        for display_text, value in enhancement_types:
            self.enhancement_type_combo.addItem(display_text, value)
        left_layout.addWidget(self.enhancement_type_combo)

        # Model selector
        model_label = QLabel("Модель для улучшения:")
        left_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.load_models()
        left_layout.addWidget(self.model_combo)

        # Enhance button
        self.enhance_btn = QPushButton("Улучшить промт")
        self.enhance_btn.clicked.connect(self.on_enhance_clicked)
        left_layout.addWidget(self.enhance_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        left_layout.addStretch()

        # Right panel: Results section
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Results tabs
        self.results_tabs = QTabWidget()

        # Tab 1: Enhanced prompt
        self.enhanced_tab = QWidget()
        enhanced_layout = QVBoxLayout(self.enhanced_tab)
        enhanced_layout.addWidget(QLabel("Улучшенный промт:"))
        self.enhanced_text = QTextEdit()
        self.enhanced_text.setReadOnly(True)
        enhanced_layout.addWidget(self.enhanced_text)

        enhanced_buttons = QHBoxLayout()
        copy_enhanced_btn = QPushButton("Копировать")
        copy_enhanced_btn.clicked.connect(self.copy_enhanced_to_clipboard)
        enhanced_buttons.addWidget(copy_enhanced_btn)

        use_enhanced_btn = QPushButton("Подставить в поле ввода")
        use_enhanced_btn.clicked.connect(self.use_enhanced_prompt)
        enhanced_buttons.addWidget(use_enhanced_btn)

        enhanced_layout.addLayout(enhanced_buttons)
        self.results_tabs.addTab(self.enhanced_tab, "Улучшенный")

        # Tab 2: Alternatives
        self.alternatives_tab = QWidget()
        alternatives_layout = QVBoxLayout(self.alternatives_tab)
        alternatives_layout.addWidget(QLabel("Альтернативные варианты:"))

        self.alternatives_list = QListWidget()
        alternatives_layout.addWidget(self.alternatives_list)

        alt_buttons = QHBoxLayout()
        copy_alt_btn = QPushButton("Копировать выбранный")
        copy_alt_btn.clicked.connect(self.copy_alternative_to_clipboard)
        alt_buttons.addWidget(copy_alt_btn)

        use_alt_btn = QPushButton("Подставить выбранный")
        use_alt_btn.clicked.connect(self.use_alternative_prompt)
        alt_buttons.addWidget(use_alt_btn)

        alternatives_layout.addLayout(alt_buttons)
        self.results_tabs.addTab(self.alternatives_tab, "Альтернативы")

        # Tab 3: Recommendations
        self.recommendations_tab = QWidget()
        recommendations_layout = QVBoxLayout(self.recommendations_tab)
        recommendations_layout.addWidget(QLabel("Объяснение и рекомендации:"))

        self.explanation_text = QTextEdit()
        self.explanation_text.setReadOnly(True)
        recommendations_layout.addWidget(QLabel("Объяснение изменений:"))
        recommendations_layout.addWidget(self.explanation_text)

        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        recommendations_layout.addWidget(QLabel("Рекомендации:"))
        recommendations_layout.addWidget(self.recommendations_text)

        self.results_tabs.addTab(self.recommendations_tab, "Рекомендации")

        self.results_tabs.setVisible(False)
        right_layout.addWidget(self.results_tabs)

        # Close button
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        right_layout.addWidget(close_btn)

        # Add panels to main layout with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        main_layout.addWidget(splitter)

    def load_models(self):
        """Load available models into the combo box."""
        try:
            models = ModelManager.get_active()
            self.model_combo.clear()
            for model in models:
                self.model_combo.addItem(model['name'], model['id'])

            if self.model_combo.count() == 0:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Нет доступных моделей. Пожалуйста, добавьте API ключи в .env файл."
                )
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки моделей: {e}")

    def on_enhance_clicked(self):
        """Handle enhance button click."""
        prompt = self.prompt_input.toPlainText().strip()

        # Validation
        if not prompt:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите промт для улучшения.")
            return

        if len(prompt) < 10:
            QMessageBox.warning(self, "Ошибка", "Промт должен содержать минимум 10 символов.")
            return

        if len(prompt) > 10000:
            QMessageBox.warning(self, "Ошибка", "Промт не должен превышать 10000 символов.")
            return

        if self.model_combo.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите модель.")
            return

        # Get inputs
        model_id = self.model_combo.currentData()
        enhancement_type = self.enhancement_type_combo.currentData()

        # Disable controls
        self.enhance_btn.setEnabled(False)
        self.prompt_input.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.enhancement_type_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # Start worker thread
        self.worker = EnhancementWorker(
            self.manager,
            prompt,
            model_id,
            enhancement_type
        )
        self.worker.finished.connect(self.on_enhancement_finished)
        self.worker.error.connect(self.on_enhancement_error)
        self.worker.start()

    def on_enhancement_finished(self, result: EnhanceResult):
        """Handle enhancement completion."""
        self.current_result = result
        self.progress_bar.setVisible(False)

        # Display results
        self.display_results(result)

        # Show results tabs
        self.results_tabs.setVisible(True)

        # Save to database
        self.manager.save_enhancement(result)

        # Re-enable controls
        self.enhance_btn.setEnabled(True)
        self.prompt_input.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.enhancement_type_combo.setEnabled(True)

        QMessageBox.information(self, "Успех", "Промт успешно улучшен!")

    def on_enhancement_error(self, error_message: str):
        """Handle enhancement error."""
        self.progress_bar.setVisible(False)

        # Re-enable controls
        self.enhance_btn.setEnabled(True)
        self.prompt_input.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.enhancement_type_combo.setEnabled(True)

        QMessageBox.critical(self, "Ошибка", error_message)

    def display_results(self, result: EnhanceResult):
        """Display enhancement results in the tabs."""
        # Enhanced prompt
        self.enhanced_text.setPlainText(result.enhanced_prompt)

        # Alternatives
        self.alternatives_list.clear()
        for alt in result.alternatives:
            self.alternatives_list.addItem(alt)

        # Explanation and recommendations
        self.explanation_text.setPlainText(result.explanation)

        recommendations_text = "Рекомендации для разных типов задач:\n\n"
        if isinstance(result.recommendations, dict):
            for task_type, recommendation in result.recommendations.items():
                recommendations_text += f"• {task_type.upper()}:\n{recommendation}\n\n"
        else:
            recommendations_text += str(result.recommendations)

        self.recommendations_text.setPlainText(recommendations_text)

    def copy_enhanced_to_clipboard(self):
        """Copy enhanced prompt to clipboard."""
        if self.current_result:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_result.enhanced_prompt)
            QMessageBox.information(self, "Успех", "Промт скопирован в буфер обмена!")

    def use_enhanced_prompt(self):
        """Use enhanced prompt in main window."""
        if self.current_result:
            self.prompt_selected.emit(self.current_result.enhanced_prompt)
            self.close()

    def copy_alternative_to_clipboard(self):
        """Copy selected alternative to clipboard."""
        if self.alternatives_list.currentItem():
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.alternatives_list.currentItem().text())
            QMessageBox.information(self, "Успех", "Вариант скопирован в буфер обмена!")

    def use_alternative_prompt(self):
        """Use selected alternative in main window."""
        if self.alternatives_list.currentItem():
            self.prompt_selected.emit(self.alternatives_list.currentItem().text())
            self.close()

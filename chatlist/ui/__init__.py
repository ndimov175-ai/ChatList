"""
User interface package for ChatList.

This package provides the PyQt6-based graphical user interface
for the ChatList application.
"""
from chatlist.ui.main_window import MainWindow
from chatlist.ui.prompt_input import PromptInputWidget
from chatlist.ui.model_selector import ModelSelectorWidget
from chatlist.ui.results_table import ResultsTableWidget
from chatlist.ui.result_comparison import ResultComparisonWidget
from chatlist.ui.settings_dialog import SettingsDialog
from chatlist.ui.model_dialog import ModelManagementDialog, ModelEditDialog

__all__ = [
    'MainWindow',
    'PromptInputWidget',
    'ModelSelectorWidget',
    'ResultsTableWidget',
    'ResultComparisonWidget',
    'SettingsDialog',
    'ModelManagementDialog',
    'ModelEditDialog',
]

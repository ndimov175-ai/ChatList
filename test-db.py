import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QLabel, QSpinBox, QMessageBox, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QComboBox
)
from PyQt6.QtCore import Qt


class DatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQLite Database Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.db_path = None
        self.conn = None
        self.current_table = None
        self.page_size = 100
        self.current_page = 0

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        file_button = QPushButton("Select SQLite File")
        file_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_button)
        layout.addLayout(file_layout)

        # Tables list
        self.tables_list = QListWidget()
        self.tables_list.itemDoubleClicked.connect(self.open_table)
        layout.addWidget(QLabel("Tables:"))
        layout.addWidget(self.tables_list)

        # Table view
        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        # Pagination
        pagination_layout = QHBoxLayout()
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(0)
        self.page_spin.valueChanged.connect(self.change_page)
        prev_button = QPushButton("Previous")
        prev_button.clicked.connect(self.prev_page)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(QLabel("Page:"))
        pagination_layout.addWidget(self.page_spin)
        pagination_layout.addWidget(prev_button)
        pagination_layout.addWidget(next_button)
        layout.addLayout(pagination_layout)

        # CRUD buttons
        crud_layout = QHBoxLayout()
        add_button = QPushButton("Add Row")
        add_button.clicked.connect(self.add_row)
        edit_button = QPushButton("Edit Row")
        edit_button.clicked.connect(self.edit_row)
        delete_button = QPushButton("Delete Row")
        delete_button.clicked.connect(self.delete_row)
        crud_layout.addWidget(add_button)
        crud_layout.addWidget(edit_button)
        crud_layout.addWidget(delete_button)
        layout.addLayout(crud_layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select SQLite File", "", "SQLite Files (*.db *.sqlite)")
        if file_path:
            self.db_path = file_path
            self.file_label.setText(file_path)
            self.load_tables()

    def load_tables(self):
        if not self.db_path:
            return
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            self.tables_list.clear()
            for table in tables:
                self.tables_list.addItem(table[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tables: {str(e)}")

    def open_table(self, item):
        self.current_table = item.text()
        self.current_page = 0
        self.load_table_data()

    def load_table_data(self):
        if not self.conn or not self.current_table:
            return
        try:
            cursor = self.conn.cursor()
            # Get column names
            cursor.execute(f"PRAGMA table_info({self.current_table})")
            columns = [col[1] for col in cursor.fetchall()]
            self.table_widget.setColumnCount(len(columns) + 1)  # +1 for rowid
            self.table_widget.setHorizontalHeaderLabels(columns + ["rowid"])

            # Get total rows
            cursor.execute(f"SELECT COUNT(*) FROM {self.current_table}")
            total_rows = cursor.fetchone()[0]
            self.total_pages = (total_rows + self.page_size - 1) // self.page_size
            self.page_spin.setMaximum(self.total_pages - 1)
            self.page_spin.setValue(self.current_page)

            # Get data for current page
            offset = self.current_page * self.page_size
            cursor.execute(f"SELECT *, rowid FROM {self.current_table} LIMIT {self.page_size} OFFSET {offset}")
            rows = cursor.fetchall()
            self.table_widget.setRowCount(len(rows))
            for row_idx, row in enumerate(rows):
                for col_idx, value in enumerate(row):
                    self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                # Hide rowid column
                self.table_widget.setColumnHidden(len(columns), True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load table data: {str(e)}")

    def change_page(self, page):
        self.current_page = page
        self.load_table_data()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.page_spin.setValue(self.current_page)
            self.load_table_data()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.page_spin.setValue(self.current_page)
            self.load_table_data()

    def add_row(self):
        if not self.conn or not self.current_table:
            return
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = cursor.fetchall()
        dialog = EditDialog(columns, self)
        if dialog.exec() == QDialog.Accepted:
            values = dialog.get_values()
            placeholders = ', '.join('?' * len(values))
            cursor.execute(f"INSERT INTO {self.current_table} VALUES ({placeholders})", values)
            self.conn.commit()
            self.load_table_data()

    def edit_row(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a row to edit.")
            return
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.current_table})")
        columns = cursor.fetchall()
        # Get current values
        values = []
        for col_idx in range(len(columns)):
            item = self.table_widget.item(current_row, col_idx)
            values.append(item.text() if item else "")
        rowid_item = self.table_widget.item(current_row, len(columns))
        rowid = rowid_item.text() if rowid_item else ""
        dialog = EditDialog(columns, self, values)
        if dialog.exec() == QDialog.Accepted:
            new_values = dialog.get_values()
            set_clause = ', '.join(f"{col[1]} = ?" for col in columns)
            cursor.execute(f"UPDATE {self.current_table} SET {set_clause} WHERE rowid = ?", new_values + [rowid])
            self.conn.commit()
            self.load_table_data()

    def delete_row(self):
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a row to delete.")
            return
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this row?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            cursor = self.conn.cursor()
            rowid_item = self.table_widget.item(current_row, self.table_widget.columnCount() - 1)
            rowid = rowid_item.text() if rowid_item else ""
            cursor.execute(f"DELETE FROM {self.current_table} WHERE rowid = ?", (rowid,))
            self.conn.commit()
            self.load_table_data()


class EditDialog(QDialog):
    def __init__(self, columns, parent=None, values=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Row")
        self.columns = columns
        self.inputs = []
        layout = QFormLayout(self)
        for i, col in enumerate(columns):
            col_name, col_type = col[1], col[2]
            input_field = QLineEdit()
            if values and i < len(values):
                input_field.setText(values[i])
            layout.addRow(f"{col_name} ({col_type}):", input_field)
            self.inputs.append(input_field)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self):
        return [inp.text() for inp in self.inputs]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = DatabaseViewer()
    viewer.show()
    sys.exit(app.exec())
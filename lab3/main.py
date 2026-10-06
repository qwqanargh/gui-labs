
import sys
from pathlib import Path

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlQueryModel, QSqlTableModel
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QTableView, QLabel,
    QPushButton, QComboBox, QHBoxLayout, QVBoxLayout, QFileDialog,
    QMessageBox, QDialog, QPlainTextEdit, QDialogButtonBox, QAction,
    QHeaderView, QSizePolicy,
)

CONNECTION = "lab3"


class QueryDialog(QDialog):
    """Модальное окно для ввода произвольного SQL-запроса."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Произвольный SQL-запрос")
        self.setModal(True)
        self.resize(480, 220)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("Например: SELECT * FROM students WHERE group_id = 3")
        self.editor.setPlainText("SELECT * FROM ")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Выполнить")
        buttons.button(QDialogButtonBox.Cancel).setText("Отмена")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Введите SQL-запрос:"))
        layout.addWidget(self.editor)
        layout.addWidget(buttons)

    def sql(self):
        return self.editor.toPlainText().strip()


class ResultTab(QWidget):
    

    def __init__(self):
        super().__init__()
        self.caption = QLabel("—")
        self.caption.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.caption.setStyleSheet("color: #555; font-family: Menlo, Consolas, monospace;")
        
        self.caption.setWordWrap(True)
        self.caption.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.view = QTableView()
        self.view.setAlternatingRowColors(True)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.view.horizontalHeader().setStretchLastSection(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.caption)
        layout.addWidget(self.view)

    def show_model(self, model, caption):
        self.view.setModel(model)
        self.caption.setText(caption)
        self.view.resizeColumnsToContents()

    def clear(self):
        self.view.setModel(None)
        self.caption.setText("—")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ЛР3 — таблицы и SQL")
        self.db = None
        self.models = []        
        self.query_counter = 0  

        self._build_menu()
        self._build_ui()
        self._set_connected(False)
        self.resize(1000, 560)

    
    def _build_menu(self):
        menu = self.menuBar().addMenu("Connection")
        self.act_set = QAction("Set connection…", self)
        self.act_set.setShortcut("Ctrl+O")
        self.act_set.triggered.connect(self.choose_database)
        self.act_close = QAction("Close connection", self)
        self.act_close.setShortcut("Ctrl+W")
        self.act_close.triggered.connect(self.close_connection)
        menu.addAction(self.act_set)
        menu.addAction(self.act_close)

        qmenu = self.menuBar().addMenu("Query")
        self.act_query = QAction("Произвольный запрос…", self)
        self.act_query.setShortcut("Ctrl+E")
        self.act_query.triggered.connect(self.custom_query)
        qmenu.addAction(self.act_query)

    def _build_ui(self):
        
        self.bt1 = QPushButton("bt1: SELECT name")
        self.bt1.setToolTip("SELECT name FROM sqlite_master → Tab2")
        self.bt1.clicked.connect(self.select_names)

        self.column_box = QComboBox()
        self.column_box.setMinimumWidth(110)
        self.column_box.setToolTip("SELECT <колонка> FROM sqlite_master → Tab3")
        self.column_box.activated[str].connect(self.select_column)

       
        self.table_box = QComboBox()
        self.table_box.setMinimumWidth(150)
        self.table_box.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.bt2 = QPushButton("bt2: данные")
        self.bt2.setToolTip("SELECT * FROM <таблица> → Tab4")
        self.bt2.clicked.connect(self.show_table_data)
        self.bt3 = QPushButton("bt3: структура")
        self.bt3.setToolTip("PRAGMA table_info(<таблица>) → Tab5")
        self.bt3.clicked.connect(self.show_table_structure)

        self.bt_query = QPushButton("Запрос…")
        self.bt_query.setToolTip("Произвольный запрос в модальном окне")
        self.bt_query.clicked.connect(self.custom_query)

        panel = QHBoxLayout()
        panel.addWidget(self.bt1)
        panel.addSpacing(12)
        panel.addWidget(QLabel("Колонка:"))
        panel.addWidget(self.column_box)
        panel.addSpacing(12)
        panel.addWidget(QLabel("Таблица:"))
        panel.addWidget(self.table_box)
        panel.addWidget(self.bt2)
        panel.addWidget(self.bt3)
        panel.addStretch()
        panel.addWidget(self.bt_query)

        # вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self._close_tab)
        self.tab = {}
        for key, title in [(1, "Tab1: sqlite_master"), (2, "Tab2: names"),
                           (3, "Tab3: column"), (4, "Tab4: data"),
                           (5, "Tab5: structure")]:
            self.tab[key] = ResultTab()
            self.tabs.addTab(self.tab[key], title)
      
        for i in range(5):
            self.tabs.tabBar().setTabButton(i, self.tabs.tabBar().RightSide, None)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addLayout(panel)
        layout.addWidget(self.tabs)
        self.setCentralWidget(central)

    def _set_connected(self, on):
        for w in (self.bt1, self.column_box, self.table_box, self.bt2, self.bt3,
                  self.bt_query, self.act_close, self.act_query):
            w.setEnabled(on)
        if not on:
            self.statusBar().showMessage("Нет соединения. Connection → Set connection…")

    
    def choose_database(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Выберите базу данных SQLite", str(Path(__file__).resolve().parent),
            "SQLite (*.db *.sqlite *.sqlite3);;Все файлы (*)")
        if path:
            self.open_database(path)

    def open_database(self, path):
        if self.db is not None:
            self.close_connection()

        db = QSqlDatabase.addDatabase("QSQLITE", CONNECTION)
        db.setDatabaseName(path)
        if not db.open():
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть БД:\n{db.lastError().text()}")
            del db
            QSqlDatabase.removeDatabase(CONNECTION)
            return
        # SQLite откроет любой файл — проверяем, что это действительно база
        check = QSqlQuery("SELECT count(*) FROM sqlite_master", db)
        if not check.isActive():
            QMessageBox.critical(self, "Ошибка", f"Файл не является базой SQLite:\n{path}")
            check.finish()
            db.close()
            del check, db
            QSqlDatabase.removeDatabase(CONNECTION)
            return
        check.finish()
        del check

        self.db = db
        self._set_connected(True)
        self.setWindowTitle(f"ЛР3 — таблицы и SQL — {Path(path).name}")

      
        model = self._query_model("SELECT * FROM sqlite_master")
        if model is None:
            return
        self.tab[1].show_model(model, "SELECT * FROM sqlite_master")
        self.tabs.setCurrentIndex(0)

        record = model.record()
        self.column_box.clear()
        self.column_box.addItems([record.fieldName(i) for i in range(record.count())])

        self.table_box.clear()
        q = QSqlQuery("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') "
                      "AND name NOT LIKE 'sqlite_%' ORDER BY type, name", self.db)
        while q.next():
            # тип объекта (table/view) храним в данных элемента списка
            self.table_box.addItem(f"{q.value(0)} ({q.value(1)})", q.value(0))
            self.table_box.setItemData(self.table_box.count() - 1, q.value(1), Qt.UserRole + 1)
        q.finish()

        self.statusBar().showMessage(f"Подключено: {Path(path).name}  |  объектов в БД: {model.rowCount()}")

    def close_connection(self):
        """Очистить все вкладки, удалить модели и закрыть соединение."""
        for t in self.tab.values():
            t.clear()
        while self.tabs.count() > 5:
            self.tabs.removeTab(5)
        for m in self.models:
            m.clear()
            m.deleteLater()
        self.models.clear()
        
        QApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.column_box.clear()
        self.table_box.clear()
        if self.db is not None:
            self.db.close()
            self.db = None
            QSqlDatabase.removeDatabase(CONNECTION)
        self.query_counter = 0
        self.setWindowTitle("ЛР3 — таблицы и SQL")
        self._set_connected(False)

    def _query_model(self, sql):
        """Выполнить запрос и вернуть QSqlQueryModel (или None при ошибке)."""
        model = QSqlQueryModel(self)
        model.setQuery(QSqlQuery(sql, self.db))
        if model.lastError().isValid():
            QMessageBox.warning(self, "Ошибка запроса", f"{sql}\n\n{model.lastError().text()}")
            model.deleteLater()
            return None
        while model.canFetchMore():  
            model.fetchMore()
        self.models.append(model)
        return model

    def _show(self, key, sql, model=None, note=""):
        model = model or self._query_model(sql)
        if model is None:
            return
        self.tab[key].show_model(model, sql + note)
        self.tabs.setCurrentWidget(self.tab[key])
        self.statusBar().showMessage(f"{sql}  →  строк: {model.rowCount()}")

    def select_names(self):
        """bt1 → Tab2."""
        self._show(2, "SELECT name FROM sqlite_master")

    def select_column(self, column):
        """Выбор колонки в QComboBox → Tab3."""
        if column:
            self._show(3, f'SELECT "{column}" FROM sqlite_master')

    def show_table_data(self):
        """bt2 → Tab4: содержимое таблицы (QSqlTableModel, можно редактировать)."""
        name = self.table_box.currentData()
        if not name:
            return
        if self.table_box.currentData(Qt.UserRole + 1) == "view":
           
            self._show(4, f'SELECT * FROM "{name}"', note="   (представление, только чтение)")
            return
        model = QSqlTableModel(self, self.db)
        model.setTable(name)
        model.setEditStrategy(QSqlTableModel.OnFieldChange)
        if not model.select():
            QMessageBox.warning(self, "Ошибка запроса", model.lastError().text())
            model.deleteLater()
            return
        while model.canFetchMore():
            model.fetchMore()
        self.models.append(model)
        self._show(4, f'SELECT * FROM "{name}"', model, note="   (ячейки можно редактировать)")

    def show_table_structure(self):
        """bt3 → Tab5: структура таблицы."""
        name = self.table_box.currentData()
        if name:
            self._show(5, f'PRAGMA table_info("{name}")')

    def custom_query(self):
        """Доп. задание: запрос в модальном окне, результат — в новой вкладке."""
        dlg = QueryDialog(self)
        if dlg.exec_() != QDialog.Accepted or not dlg.sql():
            return
        sql = dlg.sql()
        model = self._query_model(sql)
        if model is None:
            return
        self.query_counter += 1
        tab = ResultTab()
        tab.show_model(model, sql)
        index = self.tabs.addTab(tab, f"Запрос {self.query_counter}")
        self.tabs.setCurrentIndex(index)
        self.statusBar().showMessage(f"{sql}  →  строк: {model.rowCount()}")

    def _close_tab(self, index):
        if index >= 5:
            self.tabs.removeTab(index)

    def closeEvent(self, event):
        self.close_connection()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    if len(sys.argv) > 1:
        window.open_database(sys.argv[1])
    sys.exit(app.exec_())

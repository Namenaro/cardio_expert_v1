import sys
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout,
    QWidget, QHeaderView, QStyleFactory, QMenu
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPoint
from PySide6.QtGui import QColor, QBrush, QFont, QPalette, QAction
from PySide6.QtGui import QGuiApplication


class PandasModel(QAbstractTableModel):
    """Модель для отображения pandas DataFrame с подсветкой NaN"""

    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data
        self._cache = self._calculate_nan_rows()

    def _calculate_nan_rows(self):
        """Кэширует строки, содержащие NaN"""
        nan_rows = {}
        for row in range(len(self._data)):
            nan_rows[row] = self._data.iloc[row].isna().any()
        return nan_rows

    def update_data(self, new_data: pd.DataFrame):
        """Обновляет данные модели"""
        self.beginResetModel()
        self._data = new_data
        self._cache = self._calculate_nan_rows()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._data.columns)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        value = self._data.iloc[row, col]

        # Отображение текста
        if role == Qt.DisplayRole:
            if pd.isna(value):
                return "NaN"
            return str(value)

        # Подсветка фона для строк с NaN
        if role == Qt.BackgroundRole:
            if self._cache.get(row, False):
                # Проверяем, является ли текущая ячейка NaN для более яркой подсветки
                if pd.isna(value):
                    return QBrush(QColor(255, 100, 100))  # Ярко-красный для самой ячейки NaN
                return QBrush(QColor(255, 200, 200))  # Светло-красный для остальных ячеек в строке

        # Цвет текста для NaN
        if role == Qt.ForegroundRole:
            if pd.isna(value):
                return QBrush(QColor(150, 0, 0))  # Темно-красный текст

        # Выравнивание текста (числа по правому краю, текст по левому)
        if role == Qt.TextAlignmentRole:
            column_dtype = self._data.dtypes.iloc[col]
            if pd.api.types.is_numeric_dtype(column_dtype):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])

        # Стиль заголовков
        if role == Qt.FontRole:
            font = QFont()
            font.setBold(True)
            return font

        if role == Qt.BackgroundRole:
            return QBrush(QColor(240, 240, 240))

        return None

    def get_value_at(self, row: int, col: int):
        """Возвращает значение ячейки по индексам"""
        if 0 <= row < len(self._data) and 0 <= col < len(self._data.columns):
            value = self._data.iloc[row, col]
            return "NaN" if pd.isna(value) else str(value)
        return ""


class CustomTableView(QTableView):
    """Кастомная таблица с контекстным меню для копирования"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position: QPoint):
        """Показывает контекстное меню при правом клике"""
        # Получаем индекс ячейки под курсором
        index = self.indexAt(position)

        if not index.isValid():
            return

        # Создаем меню
        menu = QMenu()

        # Действие для копирования
        copy_action = QAction("Копировать", self)
        copy_action.triggered.connect(lambda: self.copy_cell_value(index))
        menu.addAction(copy_action)

        # Показываем меню
        menu.exec(self.viewport().mapToGlobal(position))

    def copy_cell_value(self, index: QModelIndex):
        """Копирует значение одной ячейки"""
        if not index.isValid():
            return

        # Получаем значение из модели
        model = self.model()
        if hasattr(model, 'get_value_at'):
            value = model.get_value_at(index.row(), index.column())
        else:
            value = index.data(Qt.DisplayRole)

        # Копируем в буфер обмена
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(str(value))


class DataFrameWidget(QWidget):
    """Виджет для отображения DataFrame с красивым оформлением"""

    def __init__(self, data: pd.DataFrame = None, parent=None):
        super().__init__(parent)

        self._data = data if data is not None else pd.DataFrame()

        # Создаем кастомную таблицу с контекстным меню
        self.table_view = CustomTableView()
        self.table_view.setAlternatingRowColors(True)  # Чередование цветов строк
        self.table_view.setSelectionBehavior(QTableView.SelectItems)  # Выделение отдельных ячеек
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)  # Множественный выбор
        self.table_view.setSortingEnabled(True)  # Включить сортировку по клику на заголовок

        # Настройка растягивания колонок
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.verticalHeader().setVisible(True)
        self.table_view.verticalHeader().setDefaultSectionSize(30)  # Высота строк

        # Устанавливаем модель
        if not self._data.empty:
            self.model = PandasModel(self._data)
            self.table_view.setModel(self.model)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Применяем стили
        self.apply_styles()

    def apply_styles(self):
        """Применяет CSS стили для таблицы"""
        self.table_view.setStyleSheet("""
            QTableView {
                background-color: white;
                gridline-color: #d0d0d0;
                selection-background-color: #cde0ff;
                selection-color: black;
                font-size: 11px;
            }

            QTableView::item:selected {
                background-color: #cde0ff;
                color: black;
            }

            QTableView::item:focus {
                outline: none;
                border: none;
            }

            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #d0d0d0;
                border-left: none;
                border-right: none;
                font-weight: bold;
                font-size: 11px;
            }

            QHeaderView::section:hover {
                background-color: #e0e0e0;
            }

            QTableView::item:hover {
                background-color: #f5f5f5;
            }

            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 12px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }

            QScrollBar:horizontal {
                border: none;
                background: #f0f0f0;
                height: 12px;
                margin: 0px;
            }

            QScrollBar::handle:horizontal {
                background: #c0c0c0;
                min-width: 20px;
                border-radius: 6px;
            }

            QScrollBar::handle:horizontal:hover {
                background: #a0a0a0;
            }
        """)

    def set_data(self, data: pd.DataFrame):
        """Обновляет данные в виджете"""
        self._data = data
        if hasattr(self, 'model'):
            self.model.update_data(data)
        else:
            self.model = PandasModel(data)
            self.table_view.setModel(self.model)

        # Настройка ширины колонок
        self.resize_columns_to_content()

    def resize_columns_to_content(self):
        """Автоматически подбирает ширину колонок под содержимое"""
        self.table_view.resizeColumnsToContents()

        # Ограничиваем максимальную ширину
        for i in range(self.model.columnCount()):
            current_width = self.table_view.columnWidth(i)
            if current_width > 300:
                self.table_view.setColumnWidth(i, 300)
            elif current_width < 60:
                self.table_view.setColumnWidth(i, 60)

    def get_data(self) -> pd.DataFrame:
        """Возвращает текущие данные"""
        return self._data


class MainWindow(QMainWindow):
    """Главное окно с примером использования"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataFrame Viewer")
        self.setGeometry(100, 100, 1000, 600)

        # Создаем пример данных с NaN
        data = self.create_sample_data()

        # Создаем виджет для отображения
        self.data_widget = DataFrameWidget(data)
        self.setCentralWidget(self.data_widget)

        # Добавляем информацию о количестве строк
        self.statusBar().showMessage(f"Всего строк: {len(data)}, Колонок: {len(data.columns)}")

    def create_sample_data(self):
        """Создает пример данных с NaN для демонстрации"""
        np.random.seed(42)

        data = {
            'Имя': ['Анна', 'Борис', 'Виктор', 'Галина', 'Дмитрий', 'Елена', 'Жанна', 'Иван'],
            'Возраст': [25, 32, 45, 28, 36, 29, 41, 33],
            'Зарплата': [50000, 65000, 80000, 55000, 72000, 58000, 69000, 47000],
            'Отдел': ['IT', 'HR', 'IT', 'Finance', 'IT', 'HR', 'Finance', 'IT'],
            'Оценка': [4.5, 4.2, np.nan, 4.8, 4.6, 4.3, np.nan, 4.1],
            'Бонус': [5000, 3000, np.nan, 4000, 6000, 3500, 4500, np.nan],
            'Город': ['Москва', 'СПб', 'Москва', 'Казань', 'Новосибирск', 'Москва', 'СПб', 'Екатеринбург']
        }

        df = pd.DataFrame(data)

        # Добавляем еще несколько строк для демонстрации скролла
        extra_data = {
            'Имя': ['Кирилл', 'Людмила', 'Михаил', 'Наталья'],
            'Возраст': [29, 38, 42, 31],
            'Зарплата': [54000, 71000, 83000, 59000],
            'Отдел': ['IT', 'HR', 'Finance', 'IT'],
            'Оценка': [4.4, np.nan, 4.7, 4.2],
            'Бонус': [5200, 3800, 5500, np.nan],
            'Город': ['Москва', 'СПб', 'Казань', 'Москва']
        }

        df_extra = pd.DataFrame(extra_data)
        df = pd.concat([df, df_extra], ignore_index=True)

        return df


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Настройка стиля приложения
    app.setStyle(QStyleFactory.create('Fusion'))

    # Устанавливаем палитру для более современного вида
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
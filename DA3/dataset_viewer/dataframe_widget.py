import pandas as pd
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPoint, QSortFilterProxyModel
from PySide6.QtGui import QColor, QBrush, QFont, QAction
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QTableView, QVBoxLayout, QWidget, QHeaderView, QMenu)

from CORE.logger import get_logger

logger = get_logger(__name__)


class PandasModel(QAbstractTableModel):
    """Модель для отображения pandas DataFrame с подсветкой NaN и нарушений"""

    def __init__(self, data: pd.DataFrame):
        super().__init__()
        self._data = data
        self._cache = self._calculate_nan_rows()
        self._violation_cache = self._calculate_violation_cells()
        # Определяем колонки с HC
        self._hc_columns = self._identify_hc_columns()

    def _identify_hc_columns(self):
        """Определяет колонки, которые начинаются с HC_"""
        hc_columns = []
        for col in self._data.columns:
            if isinstance(col, str) and col.startswith('HC_'):
                hc_columns.append(col)
        return hc_columns

    def _calculate_nan_rows(self):
        """Кэширует строки, содержащие NaN"""
        nan_rows = {}
        for row in range(len(self._data)):
            nan_rows[row] = self._data.iloc[row].isna().any()
        return nan_rows

    def _calculate_violation_cells(self):
        """
        Кэширует ячейки, содержащие нарушения (значение "нарушено")
        Возвращает словарь: (row, col) -> True, если ячейка содержит нарушение
        """
        violation_cells = {}

        for row in range(len(self._data)):
            for col in range(len(self._data.columns)):
                value = self._data.iloc[row, col]
                # Проверяем, является ли значение "нарушено"
                if isinstance(value, str) and value == "нарушено":
                    violation_cells[(row, col)] = True

        return violation_cells

    def update_data(self, new_data: pd.DataFrame):
        """Обновляет данные модели"""
        self.beginResetModel()
        self._data = new_data
        self._cache = self._calculate_nan_rows()
        self._violation_cache = self._calculate_violation_cells()
        self._hc_columns = self._identify_hc_columns()
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
        column_name = self._data.columns[col]
        is_hc_column = column_name in self._hc_columns

        # Отображение текста
        if role == Qt.DisplayRole:
            if pd.isna(value):
                return "NaN"
            return str(value)

        # Подсветка фона
        if role == Qt.BackgroundRole:
            # Для HC колонок специальная подсветка
            if is_hc_column:
                if (row, col) in self._violation_cache:
                    # Ярко-красный фон для нарушенных HC
                    return QBrush(QColor(255, 100, 100))
                elif not pd.isna(value) and str(value) == "не нарушено":
                    # Светло-зеленый фон для не нарушенных HC
                    return QBrush(QColor(200, 230, 200))

            # Для остальных колонок - проверка на NaN
            if self._cache.get(row, False):
                if pd.isna(value):
                    return QBrush(QColor(255, 100, 100))  # Ярко-красный для ячейки NaN
                return QBrush(QColor(255, 200, 200))  # Светло-красный для строк с NaN

        # Цвет текста
        if role == Qt.ForegroundRole:
            # Для нарушений в HC колонках - жирный темно-красный текст
            if is_hc_column and (row, col) in self._violation_cache:
                return QBrush(QColor(180, 0, 0))  # Темно-красный текст

            # Для NaN
            if pd.isna(value):
                return QBrush(QColor(150, 0, 0))  # Темно-красный текст для NaN

            # Для "не нарушено" в HC колонках - серый текст
            if is_hc_column and not pd.isna(value) and str(value) == "не нарушено":
                return QBrush(QColor(100, 100, 100))  # Серый текст

        # Выравнивание текста
        if role == Qt.TextAlignmentRole:
            column_dtype = self._data.dtypes.iloc[col]
            if pd.api.types.is_numeric_dtype(column_dtype):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        # Шрифт
        if role == Qt.FontRole:
            # Для нарушений в HC колонках - жирный шрифт
            if is_hc_column and (row, col) in self._violation_cache:
                font = QFont()
                font.setBold(True)
                return font

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
            column_name = self._data.columns[section] if orientation == Qt.Horizontal else None
            # Для HC колонок делаем специальный фон заголовка
            if orientation == Qt.Horizontal and column_name in self._hc_columns:
                return QBrush(QColor(255, 220, 220))  # Светло-красный фон для HC колонок
            return QBrush(QColor(240, 240, 240))

        return None

    def get_value_at(self, row: int, col: int):
        """Возвращает значение ячейки по индексам"""
        if 0 <= row < len(self._data) and 0 <= col < len(self._data.columns):
            value = self._data.iloc[row, col]
            return "NaN" if pd.isna(value) else str(value)
        return ""

    def get_raw_value(self, row: int, col: int):
        """Возвращает сырое значение для сортировки"""
        if 0 <= row < len(self._data) and 0 <= col < len(self._data.columns):
            return self._data.iloc[row, col]
        return None

class PandasSortFilterProxyModel(QSortFilterProxyModel):
    """Прокси-модель для сортировки с правильной обработкой NaN"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source_model = None

    def setSourceModel(self, source_model):
        """Устанавливает исходную модель"""
        super().setSourceModel(source_model)
        self._source_model = source_model

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        """Переопределяем метод сравнения для сортировки"""
        if not self._source_model:
            return super().lessThan(left, right)

        # Получаем сырые значения из исходной модели
        left_value = self._source_model.get_raw_value(left.row(), left.column())
        right_value = self._source_model.get_raw_value(right.row(), right.column())

        # Проверяем на NaN - NaN всегда считаем больше (чтобы они были внизу)
        left_is_na = pd.isna(left_value)
        right_is_na = pd.isna(right_value)

        # Если оба NaN - они равны
        if left_is_na and right_is_na:
            return False

        # Если левый NaN, а правый нет - левый больше (идет ниже при сортировке по возрастанию)
        if left_is_na and not right_is_na:
            return False

        # Если правый NaN, а левый нет - левый меньше (правый ниже)
        if not left_is_na and right_is_na:
            return True

        # Если оба не NaN, сравниваем как обычно
        try:
            # Пытаемся сравнивать как числа
            return float(left_value) < float(right_value)
        except (ValueError, TypeError):
            # Если не числа, сравниваем как строки
            return str(left_value).lower() < str(right_value).lower()


class CustomTableView(QTableView):
    """Кастомная таблица с контекстным меню для копирования"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.setSortingEnabled(True)

    def show_context_menu(self, position: QPoint):
        """Показывает контекстное меню при правом клике"""
        index = self.indexAt(position)

        if not index.isValid():
            return

        menu = QMenu()

        # Действие для копирования
        copy_action = QAction("Копировать", self)
        copy_action.triggered.connect(lambda: self.copy_cell_value(index))
        menu.addAction(copy_action)

        # Добавляем действие для копирования всей строки
        copy_row_action = QAction("Копировать строку", self)
        copy_row_action.triggered.connect(lambda: self.copy_row_values(index.row()))
        menu.addAction(copy_row_action)

        # Проверяем, является ли ячейка нарушением
        source_model = self.model().sourceModel() if hasattr(self.model(), 'sourceModel') else self.model()
        if hasattr(source_model, 'is_violation_cell'):
            source_row = self.model().mapToSource(index).row() if hasattr(self.model(), 'mapToSource') else index.row()
            source_col = self.model().mapToSource(index).column() if hasattr(self.model(),
                                                                             'mapToSource') else index.column()

            if source_model.is_violation_cell(source_row, source_col):
                # Добавляем информационное сообщение
                info_action = QAction("⚠️ Нарушение жесткого условия", self)
                info_action.setEnabled(False)
                menu.addSeparator()
                menu.addAction(info_action)

        menu.exec(self.viewport().mapToGlobal(position))

    def copy_cell_value(self, index: QModelIndex):
        """Копирует значение одной ячейки"""
        if not index.isValid():
            return

        value = index.data(Qt.DisplayRole)
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(str(value))

    def copy_row_values(self, row: int):
        """Копирует значения всей строки"""
        if not self.model():
            return

        row_values = []
        for col in range(self.model().columnCount()):
            index = self.model().index(row, col)
            value = index.data(Qt.DisplayRole)
            row_values.append(str(value))

        clipboard = QGuiApplication.clipboard()
        clipboard.setText("\t".join(row_values))

class DataFrameWidget(QWidget):
    """Виджет для отображения DataFrame с красивым оформлением"""

    def __init__(self, data: pd.DataFrame = None, parent=None):
        super().__init__(parent)

        self._data = data if data is not None else pd.DataFrame()

        # Создаем исходную модель
        self.source_model = PandasModel(self._data)

        # Создаем прокси-модель для сортировки
        self.proxy_model = PandasSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)

        # Создаем кастомную таблицу с контекстным меню
        self.table_view = CustomTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectItems)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)

        # Устанавливаем прокси-модель в представление
        self.table_view.setModel(self.proxy_model)

        # Настройка сортировки
        self.table_view.setSortingEnabled(True)

        # Настройка растягивания колонок
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.verticalHeader().setVisible(True)
        self.table_view.verticalHeader().setDefaultSectionSize(30)

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
        self.source_model.update_data(data)

        # Настройка ширины колонок
        self.resize_columns_to_content()

    def resize_columns_to_content(self):
        """Автоматически подбирает ширину колонок под содержимое"""
        self.table_view.resizeColumnsToContents()

        # Ограничиваем максимальную ширину
        for i in range(self.source_model.columnCount()):
            current_width = self.table_view.columnWidth(i)
            if current_width > 300:
                self.table_view.setColumnWidth(i, 300)
            elif current_width < 60:
                self.table_view.setColumnWidth(i, 60)

    def get_data(self) -> pd.DataFrame:
        """Возвращает текущие данные"""
        return self._data
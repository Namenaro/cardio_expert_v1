import sys
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout,
    QWidget, QHeaderView, QStyleFactory, QMenu
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QPoint, QSortFilterProxyModel
from PySide6.QtGui import QColor, QBrush, QFont, QPalette, QAction
from PySide6.QtGui import QGuiApplication

# Импорты для работы с вашей базой данных
from CORE.db.db_manager import DBManager
from CORE.db.forms_services import FormService
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.db_dataclasses import Form
from CORE.paths import DB_PATH
from CORE.logger import get_logger
from CORE.datasets_wrappers import LUDB

logger = get_logger(__name__)


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

        # Проверяем на NaN - NaN всегда считаем больше (чтобы они были вверху)
        left_is_na = pd.isna(left_value)
        right_is_na = pd.isna(right_value)

        # Если оба NaN - они равны
        if left_is_na and right_is_na:
            return False

        # Если левый NaN, а правый нет - левый больше (идет выше)
        if left_is_na and not right_is_na:
            return False

        # Если правый NaN, а левый нет - левый меньше (правый выше)
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
        self.setSortingEnabled(True)  # Включаем сортировку

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
        value = index.data(Qt.DisplayRole)

        # Копируем в буфер обмена
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(str(value))


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
        self.table_view.setAlternatingRowColors(True)  # Чередование цветов строк
        self.table_view.setSelectionBehavior(QTableView.SelectItems)  # Выделение отдельных ячеек
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)  # Множественный выбор

        # Устанавливаем прокси-модель в представление
        self.table_view.setModel(self.proxy_model)

        # Настройка сортировки
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(-1, Qt.AscendingOrder)  # Изначально сортировка не применена

        # Настройка растягивания колонок
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.verticalHeader().setVisible(True)
        self.table_view.verticalHeader().setDefaultSectionSize(30)  # Высота строк

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

        # Сбрасываем сортировку после обновления данных
        self.table_view.sortByColumn(-1, Qt.AscendingOrder)

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


class FormDatasetWindow(QMainWindow):
    """Главное окно с отображением параметров формы"""

    def __init__(self, form: Form, ludb: LUDB = None, parent=None):
        super().__init__(parent)

        self.form = form
        self.ludb = ludb
        self.setWindowTitle(f"Параметры формы: {form.name}")
        self.setGeometry(100, 100, 1200, 700)

        # Загружаем данные формы
        try:
            df = self.load_form_parameters(form)

            # Создаем виджет для отображения
            self.data_widget = DataFrameWidget(df)
            self.setCentralWidget(self.data_widget)

            # Добавляем информацию в статусную строку
            self.statusBar().showMessage(
                f"Форма: {form.name} | Строк: {len(df)}, Колонок: {len(df.columns)}"
            )

        except Exception as e:
            logger.exception(f"Ошибка при загрузке параметров формы {form.id}: {e}")
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")
            # Создаем пустой виджет
            self.data_widget = DataFrameWidget(pd.DataFrame())
            self.setCentralWidget(self.data_widget)

    def load_form_parameters(self, form: Form) -> pd.DataFrame:
        """
        Загружает параметры формы из базы данных

        Args:
            form: объект формы

        Returns:
            pd.DataFrame: таблица параметров
        """
        logger.info(f"Загрузка параметров формы {form.id} - {form.name}")

        # Получаем имя датасета из формы
        dataset_name = form.path_to_dataset
        if not dataset_name:
            raise ValueError(f"У формы {form.id} не указан путь к датасету")

        logger.info(f"Загрузка датасета: {dataset_name}")

        # Загружаем сырой датасет с использованием LUDB
        raw_dataset = ExemplarsDataset(
            form_dataset_name=dataset_name,
            outer_dataset=self.ludb
        )

        # Создаем параметризованный датасет
        parametrised_dataset = ParametrisedDataset(
            raw_exemplars=raw_dataset,
            form=form
        )

        # Получаем таблицу параметров
        df = parametrised_dataset.parameters_frame

        if df.empty:
            logger.warning(f"Таблица параметров для формы {form.id} пуста")
        else:
            logger.info(f"Загружено {len(df)} записей, {len(df.columns)} колонок")

        return df


if __name__ == '__main__':
    # Загружаем форму из базы данных
    db_manager = DBManager(DB_PATH)
    forms_service = FormService()

    # Создаем экземпляр LUDB
    ludb = LUDB()

    with db_manager.get_connection() as conn:
        # Получаем форму по ID
        FORM_ID = 1  # Замените на нужный ID формы
        form = forms_service.get_form_by_id(form_id=FORM_ID, conn=conn)

    # Запускаем приложение
    app = QApplication(sys.argv)

    # Настройка стиля приложения
    app.setStyle(QStyleFactory.create('Fusion'))

    # Устанавливаем палитру для более современного вида
    palette = app.palette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    app.setPalette(palette)

    # Создаем и показываем окно с формой
    window = FormDatasetWindow(form=form, ludb=ludb)
    window.show()

    sys.exit(app.exec())
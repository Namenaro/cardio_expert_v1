import sys
import pandas as pd
import numpy as np
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStyleFactory, QWidget,
    QVBoxLayout, QHBoxLayout, QScrollArea, QLabel,
    QFrame, QSizePolicy
)
from PySide6.QtCore import Qt

# Импорты для matplotlib
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from CORE.datasets_wrappers import LUDB
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.db.db_manager import DBManager
from CORE.db.forms_services import FormService
from CORE.db_dataclasses import Form
from CORE.logger import get_logger
from CORE.paths import DB_PATH
from DA3.dataset_viewer.dataframe_widget import DataFrameWidget

logger = get_logger(__name__)


class HistogramWidget(QWidget):
    """Виджет для отображения гистограммы числовых данных с использованием matplotlib"""

    def __init__(self, column_name: str, data: pd.Series, bins: int = 20, parent=None):
        super().__init__(parent)

        self.column_name = column_name
        self.data = data.dropna()  # Убираем NaN

        self.setup_ui(bins)

    def setup_ui(self, bins: int):
        """Настраивает интерфейс виджета"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Заголовок с именем колонки и количеством значений
        header = QLabel(f"<b>{self.column_name}</b>")
        header.setAlignment(Qt.AlignCenter)

        count_label = QLabel(f"Количество значений: {len(self.data)}")
        count_label.setAlignment(Qt.AlignCenter)
        count_label.setStyleSheet("color: gray; font-size: 10px;")

        layout.addWidget(header)
        layout.addWidget(count_label)

        # Создаем гистограмму
        if len(self.data) > 0:
            canvas = self.create_histogram(bins)
            layout.addWidget(canvas)
        else:
            no_data_label = QLabel("Нет числовых данных для отображения")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: gray; padding: 20px;")
            layout.addWidget(no_data_label)

        self.setLayout(layout)

        # Устанавливаем минимальную высоту
        self.setMinimumHeight(300)

    def create_histogram(self, bins: int) -> FigureCanvas:
        """Создает и возвращает виджет с гистограммой"""

        # Создаем фигуру
        fig = Figure(figsize=(5, 3), dpi=80)
        canvas = FigureCanvas(fig)

        # Создаем гистограмму
        ax = fig.add_subplot(111)
        ax.hist(self.data, bins=bins, edgecolor='black', alpha=0.7, color='steelblue')

        # Настройка внешнего вида
        ax.set_xlabel(self.column_name, fontsize=10)
        ax.set_ylabel('Частота', fontsize=10)
        ax.set_title(f'Распределение {self.column_name}', fontsize=11)
        ax.grid(True, alpha=0.3)

        # Поворачиваем подписи на оси X для лучшей читаемости
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)

        # Настройка отступов
        fig.tight_layout()

        return canvas


class StatisticsPanel(QScrollArea):
    """Панель со статистикой и гистограммами числовых колонок"""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super().__init__(parent)

        self.dataframe = dataframe
        self.setup_ui()

    def setup_ui(self):
        """Настраивает интерфейс панели"""
        # Настройка скроллинга
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Создаем контейнер для содержимого
        container = QWidget()
        self.setWidget(container)

        # Основной layout
        layout = QVBoxLayout(container)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title = QLabel("<h3>Статистика по колонкам</h3>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Находим числовые колонки
        numeric_columns = self.find_numeric_columns()

        if not numeric_columns:
            no_data_label = QLabel("Нет числовых колонок для отображения")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("color: gray; padding: 20px;")
            layout.addWidget(no_data_label)
        else:
            # Для каждой числовой колонки добавляем гистограмму
            for col in numeric_columns:
                # Создаем контейнер для гистограммы
                hist_container = QWidget()
                hist_container.setStyleSheet("""
                    QWidget {
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 5px;
                    }
                """)

                # Добавляем гистограмму
                hist_widget = HistogramWidget(col, self.dataframe[col])

                hist_layout = QVBoxLayout(hist_container)
                hist_layout.addWidget(hist_widget)
                hist_layout.setContentsMargins(10, 10, 10, 10)

                layout.addWidget(hist_container)

                # Добавляем разделитель между гистограммами
                if col != numeric_columns[-1]:
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setFrameShadow(QFrame.Sunken)
                    layout.addWidget(separator)

        # Добавляем растяжку в конец
        layout.addStretch()

        # Устанавливаем фиксированную ширину панели
        self.setFixedWidth(500)

    def find_numeric_columns(self) -> list:
        """Находит и возвращает список числовых колонок"""
        numeric_cols = []

        for col in self.dataframe.columns:
            # Пропускаем колонку с id
            if col == 'id_exemplar':
                continue

            # Проверяем тип данных колонки
            if pd.api.types.is_numeric_dtype(self.dataframe[col]):
                # Проверяем, что есть хотя бы одно числовое значение (не NaN)
                if self.dataframe[col].count() > 0:
                    numeric_cols.append(col)

        return numeric_cols

    def update_data(self, dataframe: pd.DataFrame):
        """Обновляет данные на панели"""
        self.dataframe = dataframe
        # Очищаем и пересоздаем интерфейс
        self.takeWidget().deleteLater()
        self.setup_ui()


class FormDatasetWindow(QMainWindow):
    """Главное окно с отображением параметров формы"""

    def __init__(self, form: Form, ludb: LUDB = None, parent=None):
        super().__init__(parent)

        self.form = form
        self.ludb = ludb
        self.setWindowTitle(f"Параметры формы: {form.name}")
        self.setGeometry(100, 100, 1400, 700)

        # Загружаем данные формы
        try:
            df = self.load_form_parameters(form)

            # Создаем центральный виджет с горизонтальным расположением
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # Создаем виджет для отображения таблицы
            self.data_widget = DataFrameWidget(df)
            main_layout.addWidget(self.data_widget, stretch=2)

            # Создаем панель с гистограммами
            self.stats_panel = StatisticsPanel(df)
            main_layout.addWidget(self.stats_panel, stretch=1)

            # Добавляем информацию в статусную строку
            numeric_cols_count = len(self.stats_panel.find_numeric_columns())
            self.statusBar().showMessage(
                f"Форма: {form.name} | Всего строк: {len(df)}, Колонок: {len(df.columns)} | "
                f"Числовых колонок: {numeric_cols_count}"
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

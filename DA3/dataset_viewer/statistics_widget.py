import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout, QScrollArea, QLabel,
    QFrame
)

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from CORE.logger import get_logger

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

import sys

import matplotlib
import pandas as pd
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStyleFactory, QWidget,
    QHBoxLayout, QVBoxLayout
)
from PySide6.QtWidgets import QToolBar, QPushButton, QCheckBox, QWidget, QHBoxLayout
from PySide6.QtCore import Signal, Qt

from DA3.dataset_viewer.statistics_widget import StatisticsPanel

matplotlib.use('Qt5Agg')

from CORE.datasets_wrappers.LUDB import LUDB
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.db.db_manager import DBManager
from CORE.db.forms_services import FormService
from CORE.db_dataclasses import Form
from CORE.logger import get_logger
from CORE.paths import DB_PATH
from DA3.dataset_viewer.dataframe_widget import DataFrameWidget

logger = get_logger(__name__)


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
            # Получаем параметризованный датасет
            parametrised_dataset = self.load_parametrised_dataset(form)

            # Получаем объединенный фрейм
            df = parametrised_dataset.get_merged_frame()

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

            # Подсчитываем количество нарушений
            violations_count = self.count_violations(df)
            total_violations = self.count_total_violations(df)

            self.statusBar().showMessage(
                f"Форма: {form.name} | Всего строк: {len(df)}, Колонок: {len(df.columns)} | "
                f"Числовых колонок: {numeric_cols_count} | "
                f"Строк с нарушениями: {violations_count} | "
                f"Всего нарушений: {total_violations}"
            )

        except Exception as e:
            logger.exception(f"Ошибка при загрузке параметров формы {form.id}: {e}")
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")
            # Создаем пустой виджет
            self.data_widget = DataFrameWidget(pd.DataFrame())
            self.setCentralWidget(self.data_widget)

    def load_parametrised_dataset(self, form: Form) -> ParametrisedDataset:
        """
        Загружает параметризованный датасет из базы данных

        Args:
            form: объект формы

        Returns:
            ParametrisedDataset: параметризованный датасет
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

        if parametrised_dataset.parameters_frame.empty:
            logger.warning(f"Таблица параметров для формы {form.id} пуста")
        else:
            logger.info(f"Загружено {len(parametrised_dataset.parameters_frame)} записей параметров, "
                        f"{len(parametrised_dataset.violations_frame)} записей нарушений")

        return parametrised_dataset

    def count_violations(self, df: pd.DataFrame) -> int:
        """Подсчитывает количество строк, содержащих нарушения"""
        if df.empty:
            return 0

        # Находим все колонки с нарушениями
        violation_columns = []
        for col in df.columns:
            if col != 'id_exemplar' and df[col].dtype == 'object':
                if 'нарушено' in df[col].values:
                    violation_columns.append(col)

        if not violation_columns:
            return 0

        # Подсчитываем строки, где есть хотя бы одно нарушение
        return len(df[df[violation_columns].apply(lambda row: any(row == 'нарушено'), axis=1)])

    def count_total_violations(self, df: pd.DataFrame) -> int:
        """Подсчитывает общее количество нарушений во всем датасете"""
        if df.empty:
            return 0

        total = 0
        for col in df.columns:
            if col != 'id_exemplar' and df[col].dtype == 'object':
                total += (df[col] == 'нарушено').sum()
        return total


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

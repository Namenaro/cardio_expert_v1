import random
from typing import Optional, List, Union

from CORE.datasets_wrappers import LUDB
from CORE.datasets_wrappers.form_associated.exemplars_dataset import ExemplarsDataset
from CORE.datasets_wrappers.form_associated.parametrised_dataset import ParametrisedDataset
from CORE.db.db_manager import DBManager
from CORE.db.forms_services import FormService
from CORE.db_dataclasses import Form
from CORE.logger import get_logger
from CORE.run import Exemplar
from CORE.run.exemplars_pool import ExemplarsPool
from CORE.run.r_form import RForm
from CORE.visual_debug import TrackRes, StepRes
from DA3.settings import Settings
from DA3.simulation_widgets.track_res_widget import TrackResWidget
from DA3.simulator_utils import find_track, make_interval, get_coords, exec_track

logger = get_logger(__name__)


class Simulator:
    def __init__(self):
        self.rform: Optional[RForm] = None
        self.settings = Settings()
        self.dataset: Optional[ExemplarsDataset] = None
        self._current_idx: int = -1
        self._exemplar_ids: List[str] = []
        self.ludb = LUDB()

    def _request_random_center_for_first_point(self, exemplar: Exemplar) -> Optional[float]:
        if not self.rform or not self.rform.form.points:
            return None
        first = self.rform.form.points[0].name
        coord = exemplar.get_point_coord(point_name=first)
        if coord is None:
            logger.warning(f"Точка {first} не найдена")
            return None
        delta = self.settings.max_half_padding_from_real_coord_of_first
        return random.uniform(coord - delta, coord + delta)

    def reset_form(self, form: Form):
        self.reset_dataset(name=form.path_to_dataset)
        dataset = ParametrisedDataset(form=form, raw_exemplars=self.dataset)
        try:
            evaluator = self.settings.evaluator_class(positive_dataset=dataset)
        except TypeError:
            evaluator = self.settings.evaluator_class()
        self.rform = RForm(form, evaluator=evaluator)

    def reset_dataset(self, name: str) -> None:
        if self.dataset is None or self.dataset.form_dataset_name != name:
            logger.info(f"Загрузка датасета: {name}")
            self.dataset = ExemplarsDataset(form_dataset_name=name, outer_dataset=self.ludb)
            self._exemplar_ids = self.dataset.get_all_ids()
            self._current_idx = -1
            logger.info(f"Загружено {len(self._exemplar_ids)} записей")

    def next(self) -> Optional[Exemplar]:
        if not self.dataset or self._current_idx + 1 >= len(self._exemplar_ids):
            return None
        self._current_idx += 1
        return self.dataset.get_exemplar_by_id(self._exemplar_ids[self._current_idx])

    def prev(self) -> Optional[Exemplar]:
        if not self.dataset or self._current_idx <= 0:
            return None
        self._current_idx -= 1
        return self.dataset.get_exemplar_by_id(self._exemplar_ids[self._current_idx])

    def run_track(self, ex: Exemplar, track_id: int, form: Form, center: Optional[float] = None) -> Union[
        str, TrackRes]:
        if not self.rform:
            return "Форма не инициализирована"

        track_step = find_track(form, track_id)
        if not track_step:
            return f"Трек {track_id} не найден"

        track, step = track_step

        interval = make_interval(step)
        if isinstance(interval, str):
            return interval

        if step.num_in_form == 0:
            center = center or self._request_random_center_for_first_point(ex)
            if center is None:
                return "Нет центра для первого шага"

        coords = get_coords(interval, ex, center)
        if isinstance(coords, str):
            return coords

        left, right = coords
        signal = ex.get_signal()

        return exec_track(track, signal, left, right, track_id)

    def run_step(self, ex: Exemplar, step_id: int, form: Form) -> StepRes:
        pass

    def run_form(self, ex: Exemplar, form: Form) -> ExemplarsPool:
        pass


if __name__ == "__main__":
    from CORE.paths import EXEMPLARS_DATASETS_PATH, DB_PATH
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QComboBox, \
        QLabel
    import sys
    import os

    print(f"Датасеты: {EXEMPLARS_DATASETS_PATH}")
    if os.path.exists(EXEMPLARS_DATASETS_PATH):
        print(f"Файлы: {os.listdir(EXEMPLARS_DATASETS_PATH)}")

    # Загружаем форму
    db = DBManager(DB_PATH)
    forms = FormService()

    with db.get_connection() as conn:
        form = forms.get_form_by_id(form_id=1, conn=conn)

    print(f"\nФорма: {form.name}, шагов: {len(form.steps)}")

    # Создаем симулятор
    sim = Simulator()
    sim.reset_form(form)

    if not sim._exemplar_ids:
        print("Датасет пуст!")
        sys.exit(1)

    # Получаем первый экземпляр
    first_ex = sim.next()
    if not first_ex:
        print("Не удалось получить экземпляр!")
        sys.exit(1)

    # Находим первый трек в первом шаге
    if not (form.steps and form.steps[0].tracks):
        print("В форме нет треков!")
        sys.exit(1)

    first_track_id = form.steps[0].tracks[0].id
    print(f"\nЗапуск трека {first_track_id}...")

    # Запускаем трек
    result = sim.run_track(first_ex, first_track_id, form, center=None)

    if isinstance(result, str):
        print(f"Ошибка: {result}")
        sys.exit(1)

    print(f"✅ Трек выполнен успешно!")
    print(f"  SM объектов: {len(result.sm_res_objs)}")
    print(f"  PS объектов: {len(result.ps_res_objs)}")
    print(f"  Найдено точек: {len(result.to_uniq_coords())}")
    if result.to_uniq_coords():
        print(f"  Координаты: {[f'{p:.3f}' for p in result.to_uniq_coords()]}")


    # Запускаем визуализацию
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(f"Визуализация трека {first_track_id} - Форма: {form.name}")
            self.setGeometry(100, 100, 900, 700)

            # Центральный виджет
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Основной layout
            main_layout = QVBoxLayout(central_widget)

            # Панель управления
            control_layout = QHBoxLayout()

            # Кнопка для перезапуска
            self.run_btn = QPushButton("Запустить трек")
            self.run_btn.clicked.connect(self.run_track)
            control_layout.addWidget(self.run_btn)

            # Выбор трека (если их несколько)
            self.track_combo = QComboBox()
            for i, track in enumerate(form.steps[0].tracks):
                self.track_combo.addItem(f"Трек {i + 1} (ID:{track.id})", track.id)
            control_layout.addWidget(QLabel("Выберите трек:"))
            control_layout.addWidget(self.track_combo)

            control_layout.addStretch()
            main_layout.addLayout(control_layout)

            # Информация об экземпляре
            info_text = f"Сигнал: {len(first_ex.signal)} отсчетов, {first_ex.signal.frequency} Гц"
            self.info_label = QLabel(info_text)
            main_layout.addWidget(self.info_label)

            # Виджет для визуализации
            self.track_widget = TrackResWidget()
            main_layout.addWidget(self.track_widget)

            # Сразу показываем результат
            self.track_widget.reset_data(result)

        def run_track(self):
            """Перезапускает выбранный трек"""
            track_id = self.track_combo.currentData()
            print(f"Запуск трека {track_id}...")

            result = sim.run_track(first_ex, track_id, form, center=None)

            if isinstance(result, str):
                self.info_label.setText(f"Ошибка: {result}")
            else:
                self.info_label.setText(f"✅ Успешно! Найдено точек: {len(result.to_uniq_coords())}")
                self.track_widget.reset_data(result)


    # Запускаем приложение
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

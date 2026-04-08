import random
from copy import deepcopy
from typing import Optional, List, Union

from CORE import Signal
from CORE.datasets_wrappers.ludb import LUDB
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
from CORE.visual_debug.results_datcalsses.PS_res import PS_Res
from CORE.visual_debug.results_datcalsses.SM_res import SM_Res
from DA3.settings import Settings
from DA3.simulation_app.simulator_utils import find_track, make_interval, get_coords, exec_track, \
    create_snapshot_from_step

logger = get_logger(__name__)


class Simulator:
    def __init__(self):
        self.rform: Optional[RForm] = None
        self.settings = Settings()
        self.dataset: Optional[ExemplarsDataset] = None
        self._current_idx: int = -1
        self._exemplar_ids: List[str] = []
        self.ludb = LUDB()

    def request_random_center_for_first_point(self, exemplar: Exemplar) -> Optional[float]:
        if not self.rform or not self.rform.form.points:
            return None
        first = self.rform.form.points[0].name
        coord = exemplar.get_point_coord(point_name=first)
        if coord is None:
            logger.warning(f"Точка {first} не найдена")
            return None
        delta = self.settings.max_half_padding_from_real_coord_of_first
        random_center = random.uniform(coord - delta, coord + delta)
        return random_center

    def reset_form(self, form: Form):
        self._reset_dataset(name=form.path_to_dataset)
        raw_exemplars = deepcopy(self.dataset)
        dataset = ParametrisedDataset(form=form, raw_exemplars=raw_exemplars)
        try:
            evaluator = self.settings.evaluator_class(positive_dataset=dataset)
        except TypeError:
            evaluator = self.settings.evaluator_class()
        self.rform = RForm(form, evaluator=evaluator)

    def _reset_dataset(self, name: str) -> None:
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

    def run_track(self, ex: Exemplar, track_id: int, center: Optional[float] = None) -> Union[str, TrackRes]:
        """
        Запускает указанный трек на сигнале экземпляра.

        Args:
            ex: экземпляр с сигналом и уже установленными точками
            track_id: идентификатор трека для запуска
            center: опциональный центр для первого шага

        Returns:
            Union[str, TrackRes]: результат выполнения трека или сообщение об ошибке
        """
        if not self.rform:
            return "Форма не инициализирована"

        form = self.rform.form
        track_step = find_track(form, track_id)
        if not track_step:
            return f"Трек {track_id} не найден"

        track, step = track_step

        interval = make_interval(step)
        if isinstance(interval, str):
            return interval

        if step.num_in_form == 0:
            center = center or self.request_random_center_for_first_point(ex)
            if center is None:
                return "Нет центра для первого шага"

        coords = get_coords(interval, ex, center)
        if isinstance(coords, str):
            return coords

        left, right = coords
        signal = ex.get_signal()

        return exec_track(track, signal, left, right, track_id)

    def run_step(self, ex: Exemplar, step_id: int) -> Union[str, StepRes]:
        """
        Запускает указанный шаг формы на сигнале экземпляра.

        Args:
            ex: экземпляр с сигналом и уже установленными точками
            step_id: номер шага в форме (num_in_form)

        Returns:
            Union[str, StepRes]: результат выполнения шага или сообщение об ошибке
        """
        if not self.rform:
            return "Форма не инициализирована"

        # Получаем шаг из rform
        if step_id >= len(self.rform.rsteps):
            return f"Шаг {step_id} не найден. Всего шагов: {len(self.rform.rsteps)}"

        r_step = self.rform.rsteps[step_id]

        # Для первого шага устанавливаем центр
        if step_id == 0:
            # Пытаемся получить центр через существующий метод

            center = self.request_random_center_for_first_point(ex)

            # Если не получилось (нет точек в экземпляре), используем середину сигнала
            if center is None:
                signal = ex.get_signal()
                # Берем середину сигнала в качестве центра
                center = signal.get_duration() / 2
                logger.info(f"Используем центр по умолчанию: {center:.3f} (середина сигнала)")

            r_step.set_step_as_first(center)

        try:
            # Запускаем шаг
            ex = create_snapshot_from_step(exemplar=ex, step_num=step_id, rform=self.rform, include_current_step=True)
            step_res, exemplars = r_step.run(ex, filter_by_hc=False)
            step_res.set_exemplars(exemplars)

            # Сохраняем созданные экземпляры
            self._last_step_exemplars = exemplars

            logger.info(f"Шаг {step_id} выполнен. Создано экземпляров: {len(exemplars)}")
            return step_res

        except Exception as e:
            logger.exception(f"Ошибка при выполнении шага {step_id}: {e}")
            import traceback
            traceback.print_exc()
            return f"Ошибка шага {step_id}: {e}"

    def run_form(self, big_signal: Signal, seminal_point: float) -> Union[str, ExemplarsPool]:
        """
        Запускает полный цикл распознавания формы на сигнале.

        Args:
            big_signal: сигнал, на котором будет выполняться распознавание
            seminal_point: координата во времени (секунды), куда ориентировочно помещается первая точка

        Returns:
            Union[str, ExemplarsPool]: пул итоговых экземпляров или сообщение об ошибке
        """
        if not self.rform:
            return "Форма не инициализирована"

        try:
            result_pool = self.rform.run(big_signal, seminal_point)
            logger.info(f"Форма выполнена успешно. Создано экземпляров: {len(result_pool)}")
            return result_pool

        except Exception as e:
            logger.exception(f"Ошибка при выполнении формы: {e}")
            import traceback
            traceback.print_exc()
            return f"Ошибка выполнения формы: {e}"

    def get_current_exemplar(self) -> Optional[Exemplar]:
        """Возвращает текущий экземпляр датасета"""
        if not self.dataset or self._current_idx < 0 or self._current_idx >= len(self._exemplar_ids):
            return None
        return self.dataset.get_exemplar_by_id(self._exemplar_ids[self._current_idx])

    def has_next(self) -> bool:
        """Проверяет, есть ли следующий экземпляр"""
        if not self.dataset:
            return False
        return self._current_idx + 1 < len(self._exemplar_ids)

    def has_prev(self) -> bool:
        """Проверяет, есть ли предыдущий экземпляр"""
        return self._current_idx > 0

    def run_SM(self, ex: Exemplar, sm_id: int) -> Union[str, SM_Res]:
        """
        Запускает SM-пазл (Signal Modifier) на сигнале экземпляра.

        Args:
            ex: экземпляр с сигналом и уже установленными точками
            sm_id: идентификатор SM-пазла в базе

        Returns:
            Union[str, SM_Res]: результат выполнения SM-пазла или сообщение об ошибке
        """
        if not self.rform:
            return "Форма не инициализирована"

        # Находим трек, содержащий этот SM
        found = self.rform.find_track_by_sm_id(sm_id)
        if not found:
            return f"SM с id {sm_id} не найден ни в одном треке формы"

        step_idx, track_id = found

        # Получаем центр для первого шага, если нужно
        center = None
        if step_idx == 0:
            center = self.request_random_center_for_first_point(ex)
            if center is None:
                # Если не удалось получить центр из точек, используем середину сигнала
                signal = ex.get_signal()
                center = signal.get_duration() / 2
                logger.info(f"SM {sm_id}: используем центр по умолчанию: {center:.3f}")

        # Запускаем трек
        result = self.run_track(ex, track_id, center)

        if isinstance(result, str):
            return f"Ошибка при выполнении трека для SM {sm_id}: {result}"

        # Из результатов трека извлекаем нужный SM_Res
        for sm_res in result.sm_res_objs:
            if sm_res.id == sm_id:
                return sm_res

        return f"SM с id {sm_id} не найден в результатах трека {track_id}"

    def run_PS(self, ex: Exemplar, ps_id: int) -> Union[str, PS_Res]:
        """
        Запускает PS-пазл (Point Selector) на сигнале экземпляра.

        Args:
            ex: экземпляр с сигналом и уже установленными точками
            ps_id: идентификатор PS-пазла в базе

        Returns:
            Union[str, PS_Res]: результат выполнения PS-пазла или сообщение об ошибке
        """
        if not self.rform:
            return "Форма не инициализирована"

        # Находим трек, содержащий этот PS
        found = self.rform.find_track_by_ps_id(ps_id)
        if not found:
            return f"PS с id {ps_id} не найден ни в одном треке формы"

        step_idx, track_id = found

        # Получаем центр для первого шага, если нужно
        center = None
        if step_idx == 0:
            center = self.request_random_center_for_first_point(ex)
            if center is None:
                # Если не удалось получить центр из точек, используем середину сигнала
                signal = ex.get_signal()
                center = signal.get_duration() / 2
                logger.info(f"PS {ps_id}: используем центр по умолчанию: {center:.3f}")

        # Запускаем трек
        result = self.run_track(ex, track_id, center)

        if isinstance(result, str):
            return f"Ошибка при выполнении трека для PS {ps_id}: {result}"

        # Из результатов трека извлекаем нужный PS_Res
        for ps_res in result.ps_res_objs:
            if ps_res.id == ps_id:
                return ps_res

        return f"PS с id {ps_id} не найден в результатах трека {track_id}"


if __name__ == "__main__":
    from CORE.paths import EXEMPLARS_DATASETS_PATH, DB_PATH
    from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                                   QLabel)
    import sys
    import os

    # Импортируем виджеты

    from DA3.simulation_app.simulation_widgets.step_res_widget import StepResWidget
    from DA3.simulation_app.simulation_widgets.form_res_widget import FormResWidget

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


    # ===== ТЕСТИРОВАНИЕ ШАГА =====
    print("\n" + "=" * 50)
    print("ТЕСТИРОВАНИЕ ШАГА")
    print("=" * 50)

    if not form.steps:
        print("В форме нет шагов!")
    else:
        first_step_id = form.steps[0].num_in_form
        target_point_name = form.steps[0].target_point.name if form.steps[0].target_point else 'не указана'
        print(f"Запуск шага {first_step_id} (цель: {target_point_name})...")
        print(f"  Треков в шаге: {len(form.steps[0].tracks)}")

        # СОЗДАЕМ НОВЫЙ ЧИСТЫЙ ЭКЗЕМПЛЯР БЕЗ ТОЧЕК
        # Получаем сырой сигнал из существующего экземпляра
        raw_signal = first_ex.get_signal()

        # Создаем новый экземпляр только с сигналом, без точек
        from CORE.run import Exemplar

        clean_ex = Exemplar(signal=raw_signal)

        # Запускаем шаг на чистом экземпляре
        step_result = sim.run_step(clean_ex, first_step_id)

        if isinstance(step_result, str):
            print(f"Ошибка шага: {step_result}")
        else:
            print(f"✅ Шаг выполнен успешно!")
            print(f"  ID шага: {step_result.id}")
            print(f"  Интервал: [{step_result.left_coord:.3f}, {step_result.right_coord:.3f}]")
            print(f"  Результатов треков: {len(step_result.tracks_results)}")

            # Собираем все точки из всех треков
            all_points = []
            for i, track_res in enumerate(step_result.tracks_results):
                points = track_res.to_uniq_coords()
                all_points.extend(points)
                print(f"    Трек {i + 1} (ID:{track_res.id}): {len(points)} точек")
                if points:
                    print(f"      Координаты: {[f'{p:.3f}' for p in points]}")

            print(f"  Всего уникальных точек: {len(set(all_points))}")
            if all_points:
                print(f"  Примеры координат: {[f'{p:.3f}' for p in sorted(set(all_points))[:5]]}")


            # Запускаем визуализацию шага
            class StepWindow(QMainWindow):
                def __init__(self):
                    super().__init__()
                    self.setWindowTitle(f"Визуализация шага {first_step_id} - Форма: {form.name}")
                    self.setGeometry(100, 100, 1000, 700)

                    central_widget = QWidget()
                    self.setCentralWidget(central_widget)
                    layout = QVBoxLayout(central_widget)

                    # Информация
                    info_text = f"Шаг {first_step_id} | Цель: {target_point_name}\n"
                    info_text += f"Сигнал: {len(raw_signal)} отсчетов, {raw_signal.frequency} Гц\n"
                    info_text += f"Интервал поиска: [{step_result.left_coord:.3f}, {step_result.right_coord:.3f}]"

                    info_label = QLabel(info_text)
                    info_label.setWordWrap(True)
                    layout.addWidget(info_label)

                    # Виджет шага
                    self.step_widget = StepResWidget()
                    layout.addWidget(self.step_widget)

                    # Показываем результаты
                    self.step_widget.reset_data(step_result)


            step_app = QApplication.instance() or QApplication(sys.argv)
            step_window = StepWindow()
            step_window.show()
            step_app.exec()

    # ===== ТЕСТИРОВАНИЕ ФОРМЫ =====
    print("\n" + "=" * 50)
    print("ТЕСТИРОВАНИЕ ФОРМЫ")
    print("=" * 50)

    # Получаем сигнал из первого экземпляра
    signal = first_ex.get_signal()

    # Определяем семинальную точку (середина сигнала)
    seminal_point = signal.get_duration() / 2
    print(f"Запуск формы с семинальной точкой: {seminal_point:.3f}...")

    # Запускаем форму
    form_result = sim.run_form(signal, seminal_point)

    if isinstance(form_result, str):
        print(f"Ошибка формы: {form_result}")
    else:
        print(f"✅ Форма выполнена успешно!")
        print(f"  Создано экземпляров: {len(form_result)}")

        # Выводим информацию о лучших экземплярах
        if form_result.exemplars_sorted:
            print(f"\nТоп-3 лучших экземпляра:")
            for i, ex in enumerate(form_result.exemplars_sorted[:3]):
                print(f"  {i + 1}. Оценка: {ex.evaluation_result:.3f}")
                print(
                    f"     Точки: {sorted([(name, coord) for name, (coord, _) in ex._points.items()], key=lambda x: x[1])}")


        # Запускаем визуализацию формы
        class FormWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle(f"Визуализация формы {form.name}")
                self.setGeometry(100, 100, 1200, 800)

                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)

                # Информация
                info_text = f"Форма: {form.name}\n"
                info_text += f"Сигнал: {len(signal)} отсчетов, {signal.frequency} Гц\n"
                info_text += f"Семинальная точка: {seminal_point:.3f}\n"
                info_text += f"Всего экземпляров в пуле: {len(form_result)}"

                info_label = QLabel(info_text)
                info_label.setWordWrap(True)
                layout.addWidget(info_label)

                # Виджет формы
                self.form_widget = FormResWidget(padding_percent=20)
                layout.addWidget(self.form_widget)

                # Показываем результаты (без ground truth, так как его нет)
                self.form_widget.reset_data(form_result, ground_truth=None)


        form_app = QApplication.instance() or QApplication(sys.argv)
        form_window = FormWindow()
        form_window.show()
        form_app.exec()

    print("\n✅ Все тесты завершены!")

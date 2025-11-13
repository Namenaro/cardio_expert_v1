from CORE.db_dataclasses import Form, Track, Point,  Parameter, BaseClass, Step, BasePazzle, CLASS_TYPES, DATA_TYPES
from CORE.database.db_manager import DBManager
from CORE.database.repositories import *
from CORE.database.repositories.objects_helpers_repos import *


import sqlite3

from typing import List, Optional, Dict
import logging


class FormsService:
    """Расширенный сервис для работы с формами и всеми связанными сущностями"""

    def __init__(self, db: 'DBManager'):
        self.db = db
        self._simple_forms_repo = FormsSimpleRepo()
        self._points_repo = PointsRepo()
        self._params_repo = ParamsRepo()
        self._objects_repo = ObjectsRepo()
        self._objects_service = ObjectsService()
        self._steps_repo = StepsRepo()

    # Методы для работы с записями таблицы form (только основная информация)
    def get_all_form_entries(self) -> List[Form]:
        """Получить все записи форм (только основная информация)"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.get_all_forms(conn)

    def get_form_entry_by_id(self, form_id: int) -> Optional[Form]:
        """Получить запись формы по ID (только основная информация)"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.get_form_by_id(conn, form_id)

    def add_form_entry(self, form: Form) -> Optional[int]:
        """Добавить запись формы (только основная информация)"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.add_form(conn, form)

    def update_form_entry(self, form: Form) -> bool:
        """Обновить запись формы (только основная информация)"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.update_form(conn, form)

    def delete_form_entry(self, form_id: int) -> bool:
        """Удалить запись формы по ID (только основная информация)"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.delete_form_by_id(conn, form_id)

    # Методы для работы с полными формами (со всем содержимым)
    def add_form(self, form: Form) -> Optional[int]:
        """Добавить форму со всем ее содержимым (точками, параметрами, объектами, шагами)"""
        with self.db.get_connection() as conn:
            try:

                # Создаем базовую запись формы
                form_id = self._simple_forms_repo.add_form(conn, form)
                if form_id is None:
                    conn.rollback()
                    return None
                form.form_id = form_id

                # Добавляем точки формы
                for point in form.points:
                    point_id = self._points_repo.add_new_point(conn, form_id, point)
                    point.id = point_id
                    if point_id is None:
                        conn.rollback()
                        return None


                # Добавляем параметры формы
                for parameter in form.parameters:
                    param_id = self._params_repo.add_new_parameter(conn, form_id, parameter)
                    parameter.id = param_id
                    if param_id is None:
                        conn.rollback()
                        return None

                # Создаем объекты HC/PC
                # Привязываем созданные объекты HC/PC к форме
                for obj in form.HC_PC_objects:
                    obj_id = self._objects_repo.add_object_to_form(conn, form_id, obj.id)
                    if obj_id is None:
                        conn.rollback()
                        return None


                # Добавляем шаги с треками и объектами
                for step_index, step in enumerate(form.steps):
                    # Проверяем, что целевая точка существует и имеет ID
                    if not step.target_point or not step.target_point.id:
                        print(f"Ошибка: целевая точка шага {step_index} не определена")
                        conn.rollback()
                        return None

                    # Создаем шаг
                    step_id = self._steps_repo.add_step(
                        conn, form_id,
                        step.target_point.id,
                        step.left_point.id if step.left_point else None,
                        step.right_point.id if step.right_point else None,
                        step.left_padding_t,
                        step.right_padding_t,
                        step.comment,
                        step_index  # num_in_form
                    )
                    if step_id is None:
                        conn.rollback()
                        return None

                    # Добавляем треки шага
                    for track_index, track in enumerate(step.tracks):
                        track_id = self._steps_repo.add_track(conn, step_id)
                        if track_id is None:
                            conn.rollback()
                            return None

                        # Добавляем SM объекты в трек
                        for sm_index, sm_obj in enumerate(track.SMs):
                            if sm_obj.id:
                                relation_id = self._steps_repo.add_object_to_track(
                                    conn, track_id, sm_obj.id, sm_index
                                )
                                if relation_id is None:
                                    conn.rollback()
                                    return None
                            else:
                                print(f"Предупреждение: SM объект не имеет ID, пропускаем")

                        # Добавляем PS объекты в трек (после SM)
                        ps_start_index = len(track.SMs)
                        for ps_index, ps_obj in enumerate(track.PSs):
                            if ps_obj.id:
                                relation_id = self._steps_repo.add_object_to_track(
                                    conn, track_id, ps_obj.id, ps_start_index + ps_index
                                )
                                if relation_id is None:
                                    conn.rollback()
                                    return None
                            else:
                                print(f"Предупреждение: PS объект не имеет ID, пропускаем")

                conn.commit()
                return form_id

            except sqlite3.Error as e:
                conn.rollback()
                print(f"Ошибка при добавлении формы с содержимым: {e}")
                return None

    def get_form(self, form_id: int) -> Optional[Form]:
        """Получить полную форму со всем содержимым"""
        with self.db.get_connection() as conn:
            # Получаем базовую информацию о форме
            form = self._simple_forms_repo.get_form_by_id(conn, form_id)
            if not form:
                return None

            # Получаем точки формы
            form.points = self._points_repo.read_all_points_by_form_id(conn, form_id)

            # Получаем параметры формы
            form.parameters = self._params_repo.read_all_parameters_by_form_id(conn, form_id)

            # Получаем объекты HC/PC, связанные с формой
            object_ids = self._objects_repo.get_objects_by_form(conn, form_id)
            form.HC_PC_objects = []
            for obj_id in object_ids:
                full_obj = self._objects_service.get_full_object(conn, obj_id)
                if full_obj:
                    form.HC_PC_objects.append(full_obj)

            # Получаем шаги формы с полной информацией
            steps = self._steps_repo.get_steps_by_form(conn, form_id)

            # Заполняем дополнительную информацию для шагов
            for step in steps:
                if step.id:
                    # Получаем треки шага
                    tracks = self._steps_repo.get_tracks_by_step(conn, step.id)

                    # Для каждого трека получаем объекты и разделяем их на SM и PS
                    for track in tracks:
                        if track.id:
                            objects = self.get_objects_by_track(track.id)
                            for obj in objects:
                                # Определяем тип объекта (SM или PS)
                                if obj.class_ref and obj.class_ref.type == "SM":
                                    track.SMs.append(obj)
                                elif obj.class_ref and obj.class_ref.type == "PS":
                                    track.PSs.append(obj)

                    step.tracks = tracks

            form.steps = steps
            return form

    def delete_form(self, form_id: int) -> bool:
        """Удалить полную форму со всеми связанными сущностями"""
        with self.db.get_connection() as conn:
            try:
                # Удаляем шаги и их связи
                self._steps_repo.delete_all_steps_of_form(conn, form_id)

                # Удаляем точки формы
                self._points_repo.delete_all_points_of_form(conn, form_id)

                # Удаляем параметры формы
                self._params_repo.delete_all_parameters_of_form(conn, form_id)

                # Удаляем связи с объектами HC/PC
                self._objects_repo.delete_all_objects_from_form(conn, form_id)

                # Удаляем саму запись формы
                result = self._simple_forms_repo.delete_form_by_id(conn, form_id)
                conn.commit()
                return result
            except sqlite3.Error as e:
                print(f"Ошибка при удалении формы: {e}")
                conn.rollback()
                return False

    # Методы для работы с отдельными компонентами формы остаются без изменений
    def add_point(self, form_id: int, point: Point) -> Optional[int]:
        """Добавить точку к форме"""
        with self.db.get_connection() as conn:
            return self._points_repo.add_new_point(conn, form_id, point)

    def get_points_by_form(self, form_id: int) -> List[Point]:
        """Получить все точки формы"""
        with self.db.get_connection() as conn:
            return self._points_repo.read_all_points_by_form_id(conn, form_id)

    def update_point(self, point: Point) -> bool:
        """Обновить точку"""
        with self.db.get_connection() as conn:
            return self._points_repo.update_point(conn, point)

    def delete_point(self, point_id: int) -> bool:
        """Удалить точку по ID"""
        with self.db.get_connection() as conn:
            return self._points_repo.delete_point_by_id(conn, point_id)

    def add_parameter(self, form_id: int, parameter: Parameter) -> Optional[int]:
        """Добавить параметр к форме"""
        with self.db.get_connection() as conn:
            return self._params_repo.add_new_parameter(conn, form_id, parameter)

    def get_parameters_by_form(self, form_id: int) -> List[Parameter]:
        """Получить все параметры формы"""
        with self.db.get_connection() as conn:
            return self._params_repo.read_all_parameters_by_form_id(conn, form_id)

    def update_parameter(self, parameter: Parameter) -> bool:
        """Обновить параметр"""
        with self.db.get_connection() as conn:
            return self._params_repo.update_parameter(conn, parameter)

    def delete_parameter(self, parameter_id: int) -> bool:
        """Удалить параметр по ID"""
        with self.db.get_connection() as conn:
            return self._params_repo.delete_parameter_by_id(conn, parameter_id)

    # Методы для работы с объектами HC/PC
    def add_object_to_form(self, form_id: int, object_id: int) -> bool:
        """Добавляет объект к форме"""
        with self.db.get_connection() as conn:
            result = self._objects_repo.add_object_to_form(conn, form_id, object_id)
            return result is not None

    def get_form_objects(self, form_id: int) -> List[BasePazzle]:
        """Получает список объектов, связанных с формой"""
        with self.db.get_connection() as conn:
            object_ids = self._objects_repo.get_objects_by_form(conn, form_id)
            objects = []
            for obj_id in object_ids:
                obj = self._objects_service.get_full_object(conn, obj_id)
                if obj:
                    objects.append(obj)
            return objects

    # Методы для работы с шагами
    def add_step(self, form_id: int, target_point_id: int,
                 left_point_id: Optional[int] = None, right_point_id: Optional[int] = None,
                 left_padding: Optional[float] = None, right_padding: Optional[float] = None,
                 comment: str = "", num_in_form: int = 0) -> Optional[int]:
        """Добавляет шаг к форме"""
        with self.db.get_connection() as conn:
            return self._steps_repo.add_step(conn, form_id, target_point_id, left_point_id,
                                             right_point_id, left_padding, right_padding,
                                             comment, num_in_form)

    def get_steps_by_form(self, form_id: int) -> List[Step]:
        """Получает все шаги формы"""
        with self.db.get_connection() as conn:
            return self._steps_repo.get_steps_by_form(conn, form_id)

# Пример использования
if __name__ == "__main__":
    from CORE.database.repositories.classes_repo_write import add_all_classes_to_db
    db_manager = DBManager()

    if db_manager.db_exists():
        db_manager.delete_database()
    db_manager.create_tables()
    add_all_classes_to_db(db_manager)


    servise = FormsService(db_manager)

    test_form = Form(name="test_form",
                     comment="комментарий",
                     path_to_pic="\путь к картике",
                     path_to_dataset="\путь к датасету")

    id = servise.add_form(test_form)
    print(id)

    point_id_1 = servise.add_point(form_id=id, point=Point(name="point_1", comment="коммент о точке"))
    point_id_2 = servise.add_point(form_id=id, point=Point(name="point_2", comment="коммент о точке"))


    parameter_1 = servise.add_parameter(form_id=id, parameter=Parameter(name="param_1", comment="коммент о параметре", data_type=DATA_TYPES.INT.value))
    parameter_2 = servise.add_parameter(form_id=id, parameter=Parameter(name="param_2", comment="коммент о параметре",
                                                                        data_type=DATA_TYPES.FLOAT.value))

    servise.delete_parameter(parameter_id=parameter_1)



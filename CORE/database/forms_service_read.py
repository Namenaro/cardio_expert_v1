from CORE.db_dataclasses import Form, Track, Point,  Parameter, BaseClass, Step, BasePazzle, CLASS_TYPES, DATA_TYPES
from CORE.database.db_manager import DBManager
from CORE.database.repositories import *
from CORE.database.repositories.values_repos import *


import sqlite3

from typing import List, Optional, Dict
import logging
from copy import deepcopy


class FormsServiceRead:
    """Расширенный сервис для работы с формами и всеми связанными сущностями"""

    def __init__(self, db: 'DBManager'):
        self.db = db
        self._simple_forms_repo = FormsSimpleRepo()
        self._points_repo = PointsRepo()
        self._params_repo = ParamsRepo()
        self._objects_repo = ObjectsSimpleRepo()
        self._objects_service = ObjectsService()
        self._steps_repo = StepsRepo()


    def get_all_form_entries(self) -> List[Form]:
        """Получить все записи форм (только основная информация)"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.get_all_forms(conn)


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
            object_ids = self._objects_repo.get_objects_ids_by_form(conn, form_id)
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



    def get_points_by_form(self, form_id: int) -> List[Point]:
        """Получить все точки формы"""
        with self.db.get_connection() as conn:
            return self._points_repo.read_all_points_by_form_id(conn, form_id)


    def get_parameters_by_form(self, form_id: int) -> List[Parameter]:
        """Получить все параметры формы"""
        with self.db.get_connection() as conn:
            return self._params_repo.read_all_parameters_by_form_id(conn, form_id)


    def get_form_objects(self, form_id: int) -> List[BasePazzle]:
        """Получает список объектов, связанных с формой"""
        with self.db.get_connection() as conn:
            object_ids = self._objects_repo.get_objects_ids_by_form(conn, form_id)
            objects = []
            for obj_id in object_ids:
                obj = self._objects_service.get_full_object(conn, obj_id)
                if obj:
                    objects.append(obj)
            return objects


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


    servise = FormsServiceRead(db_manager)

    form = servise.get_form(form_id=0)
    print(form)


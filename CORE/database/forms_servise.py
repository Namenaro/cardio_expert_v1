from CORE.db_dataclasses import Form, Track, Point,  Parameter, BaseClass, BasePazzle, CLASS_TYPES, DATA_TYPES
from CORE.database.db_manager import DBManager
from CORE.database.repositories import *


import sqlite3

from typing import List, Optional, Dict
import logging


class FormsService:
    def __init__(self, db: 'DBManager') -> None:
        self.db = db
        self._points_repo = PointsRepo()
        self._simple_forms_repo = FormsSimpleRepo()
        self._params_repo = ParamsRepo()

    # Методы для работы с формами
    def get_all_forms(self) -> List[Form]:
        """Получить все формы"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.get_all_forms(conn)

    def get_form_by_id(self, form_id: int) -> Optional[Form]:
        """Получить форму по ID"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.get_form_by_id(conn, form_id)

    def add_form(self, form: Form) -> Optional[int]:
        """Добавить новую форму"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.add_form(conn, form)

    def update_form(self, form: Form) -> bool:
        """Обновить форму"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.update_form(conn, form)

    def delete_form(self, form_id: int) -> bool:
        """Удалить форму по ID"""
        with self.db.get_connection() as conn:
            return self._simple_forms_repo.delete_form_by_id(conn, form_id)

    # Методы для работы с точками
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

    def delete_all_points_of_form(self, form_id: int) -> bool:
        """Удалить все точки формы"""
        with self.db.get_connection() as conn:
            return self._points_repo.delete_all_points_of_form(conn, form_id)

    # Методы для работы с параметрами
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

    def delete_all_parameters_of_form(self, form_id: int) -> bool:
        """Удалить все параметры формы"""
        with self.db.get_connection() as conn:
            return self._params_repo.delete_all_parameters_of_form(conn, form_id)

    # Комплексные операции
    def get_form_with_details(self, form_id: int) -> Optional[dict]:
        """Получить форму со всеми точками и параметрами"""
        with self.db.get_connection() as conn:
            form = self._simple_forms_repo.get_form_by_id(conn, form_id)
            if not form:
                return None

            points = self._points_repo.read_all_points_by_form_id(conn, form_id)
            parameters = self._params_repo.read_all_parameters_by_form_id(conn, form_id)

            return {
                'form': form,
                'points': points,
                'parameters': parameters
            }

    def delete_form_completely(self, form_id: int) -> bool:
        """Полностью удалить форму со всеми точками и параметрами"""
        with self.db.get_connection() as conn:
            try:
                # Удаляем точки формы
                self._points_repo.delete_all_points_of_form(conn, form_id)
                # Удаляем параметры формы
                self._params_repo.delete_all_parameters_of_form(conn, form_id)
                # Удаляем саму форму
                result = self._simple_forms_repo.delete_form_by_id(conn, form_id)
                conn.commit()
                return result
            except sqlite3.Error as e:
                conn.rollback()
                print(f"Ошибка при полном удалении формы: {e}")
                return False

    def create_form_with_data(self, form: Form, points: List[Point], parameters: List[Parameter]) -> Optional[int]:
        """Создать форму с точками и параметрами в одной транзакции"""
        with self.db.get_connection() as conn:
            try:
                # Создаем форму
                form_id = self._simple_forms_repo.add_form(conn, form)
                if form_id is None:
                    conn.rollback()
                    return None

                # Добавляем точки
                for point in points:
                    point_id = self._points_repo.add_new_point(conn, form_id, point)
                    if point_id is None:
                        conn.rollback()
                        return None

                # Добавляем параметры
                for parameter in parameters:
                    param_id = self._params_repo.add_new_parameter(conn, form_id, parameter)
                    if param_id is None:
                        conn.rollback()
                        return None

                conn.commit()
                return form_id
            except sqlite3.Error as e:
                conn.rollback()
                print(f"Ошибка при создании формы с данными: {e}")
                return None

    def copy_form(self, source_form_id: int, new_form_name: str) -> Optional[int]:
        """Скопировать форму со всеми точками и параметрами"""
        with self.db.get_connection() as conn:
            try:
                # Получаем исходную форму
                source_form = self._simple_forms_repo.get_form_by_id(conn, source_form_id)
                if not source_form:
                    return None

                # Создаем новую форму
                new_form = Form(
                    name=new_form_name,
                    comment=f"Копия: {source_form.comment}",
                    path_to_pic=source_form.path_to_pic,
                    path_to_dataset=source_form.path_to_dataset
                )

                new_form_id = self._simple_forms_repo.add_form(conn, new_form)
                if new_form_id is None:
                    conn.rollback()
                    return None

                # Копируем точки
                source_points = self._points_repo.read_all_points_by_form_id(conn, source_form_id)
                for point in source_points:
                    new_point = Point(name=point.name, comment=point.comment)
                    if self._points_repo.add_new_point(conn, new_form_id, new_point) is None:
                        conn.rollback()
                        return None

                # Копируем параметры
                source_parameters = self._params_repo.read_all_parameters_by_form_id(conn, source_form_id)
                for param in source_parameters:
                    new_param = Parameter(
                        name=param.name,
                        comment=param.comment,
                        data_type=param.data_type
                    )
                    if self._params_repo.add_new_parameter(conn, new_form_id, new_param) is None:
                        conn.rollback()
                        return None

                conn.commit()
                return new_form_id
            except sqlite3.Error as e:
                conn.rollback()
                print(f"Ошибка при копировании формы: {e}")
                return None

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



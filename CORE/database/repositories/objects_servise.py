import sqlite3
from typing import Optional, List
from CORE.database.repositories.values_repos import *
from CORE.db_dataclasses import BasePazzle

import logging


logger = logging.getLogger(__name__)


class ObjectsService:
    """Фасадный сервис для работы со всеми репозиториями объектов"""

    def __init__(self):
        self._objects_repo = ObjectsSimpleRepo()
        self._argument_values_repo = ArgumentValuesRepo()
        self._input_param_values_repo = InputParamValuesRepo()
        self._input_point_values_repo = InputPointValuesRepo()
        self._output_param_values_repo = OutputParamValuesRepo()

    def get_full_object(self, conn: sqlite3.Connection, object_id: int) -> Optional[BasePazzle]:
        """Получает полную информацию об объекте со всеми связанными значениями"""
        obj = self._objects_repo.get_object_entry_by_id(conn, object_id)
        if not obj:
            return None

        # Загружаем все связанные значения
        obj.argument_values = self._argument_values_repo.get_argument_values_by_object(conn, object_id)
        obj.input_param_values = self._input_param_values_repo.get_input_param_values_by_object(conn, object_id)
        obj.input_point_values = self._input_point_values_repo.get_input_point_values_by_object(conn, object_id)
        obj.output_param_values = self._output_param_values_repo.get_output_param_values_by_object(conn, object_id)

        return obj

    def delete_object_completely(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Полностью удаляет объект и все связанные с ним данные
        Управление транзакцией осуществляется вызывающим кодом.
        Метод только выполняет операции в рамках существующей транзакции.
        """
        logger.info(f"Начато удаление объекта {object_id} и связанных данных")

        # Удаляем все связанные значения
        repositories = [
            ("аргументов", self._argument_values_repo.delete_all_argument_values_by_object),
            ("входных параметров", self._input_param_values_repo.delete_all_input_param_values_by_object),
            ("входных точек", self._input_point_values_repo.delete_all_input_point_values_by_object),
            ("выходных параметров", self._output_param_values_repo.delete_all_output_param_values_by_object)
        ]

        for data_type, delete_method in repositories:
            delete_method(conn, object_id)
            logger.debug(f"Удалены данные {data_type} для объекта {object_id}")

        # Удаляем сам объект
        result = self._objects_repo.delete_object(conn, object_id)

        if result:
            logger.info(f"Объект {object_id} и все связанные данные помечены для удаления")
        else:
            logger.warning(f"Основной объект {object_id} не найден")

        return result

    def add_full_object(self, conn: sqlite3.Connection, object:BasePazzle):
        """Добавляет всю информацию об объекте со всеми связанными значениями.
        Управление транзакцией осуществляется вызывающим кодом."""
        arg_vals_ids = []
        input_param_vals_ids = []
        input_point_vals_ids = []
        output_param_vals_ids = []

        try:
            obj_id = self._objects_repo.add_object_entry(conn, object=object)

            # Добавляем аргументы конструктора
            for arg_val in object.argument_values:
                arg_val_id = self._argument_values_repo.add_argument_value(conn=conn, object_id=obj_id, value=arg_val)
                arg_vals_ids.append(arg_val_id)

            # Добавляем входные параметры
            for input_param_val in object.input_param_values:
                inp_param_id = self._input_param_values_repo.add_input_param_value(conn=conn, object_id=obj_id, value=input_param_val)
                input_param_vals_ids.append(inp_param_id)

            # Добавляем входные точки
            for input_point_val in object.input_point_values:
                inp_point_id = self._input_point_values_repo.add_input_point_value(conn=conn, object_id=obj_id, value=input_point_val)
                input_point_vals_ids.append(inp_point_id)

            # Добавляем выходные параметры
            for output_param_val in object.output_param_values:
                out_param_id = self._output_param_values_repo.add_output_param_value(conn=conn, object_id=obj_id, value=output_param_val)
                output_param_vals_ids.append(out_param_id)

        except sqlite3.Error as e:
            print(f"Ошибка при полном удалении объекта: {e}")
            raise

        return obj_id, arg_vals_ids, input_param_vals_ids, input_point_vals_ids, output_param_vals_ids





from CORE.db_dataclasses import *

import logging
from typing import List, Optional

class ObjectDataService:
    """
    Сервис для управления связанными данными объектов в таблицах value_to_*.
    Обеспечивает операции добавления, обновления и удаления значений аргументов,
    входных/выходных параметров и точек для объектов BasePazzle.
    Содержит методы для точечного обновления данных при сохранении класса объекта.
    """

    def __init__(self):
        pass

    def _add_related_data(self, cursor, object_id: int, base_pazzle: BasePazzle):
        """Добавляет все связанные данные объекта"""
        # Добавляем значения аргументов
        for arg_value in base_pazzle.argument_values:
            cursor.execute('''
                INSERT INTO value_to_argument (object_id, argument_id, argument_value)
                VALUES (?, ?, ?)
            ''', (object_id, arg_value.argument_id, arg_value.argument_value))
            arg_value.id = cursor.lastrowid

        # Добавляем значения входных параметров
        for input_param in base_pazzle.input_param_values:
            cursor.execute('''
                INSERT INTO value_to_input_param (object_id, input_param_id, parameter_id)
                VALUES (?, ?, ?)
            ''', (object_id, input_param.input_param_id, input_param.parameter_id))
            input_param.id = cursor.lastrowid

        # Добавляем значения входных точек
        for input_point in base_pazzle.input_point_values:
            cursor.execute('''
                INSERT INTO value_to_input_point (object_id, input_point_id, point_id)
                VALUES (?, ?, ?)
            ''', (object_id, input_point.input_point_id, input_point.point_id))
            input_point.id = cursor.lastrowid

        # Добавляем значения выходных параметров
        for output_param in base_pazzle.output_param_values:
            cursor.execute('''
                INSERT INTO value_to_output_param (object_id, output_param_id, parameter_id)
                VALUES (?, ?, ?)
            ''', (object_id, output_param.output_param_id, output_param.parameter_id))
            output_param.id = cursor.lastrowid

    def _delete_related_data(self, cursor, object_id: int):
        """Удаляет все связанные данные объекта"""
        tables_to_clear = [
            'value_to_argument',
            'value_to_input_param',
            'value_to_input_point',
            'value_to_output_param'
        ]

        for table in tables_to_clear:
            cursor.execute(f"DELETE FROM {table} WHERE object_id = ?", (object_id,))

    def _update_related_data(self, cursor, object_id: int, new_object: BasePazzle, current_object: BasePazzle):
        """
        Точечно обновляет связанные данные объекта когда класс не изменился
        """
        # Создаем словари для быстрого поиска существующих записей
        current_args = {arg.argument_id: arg for arg in current_object.argument_values}
        current_input_params = {param.input_param_id: param for param in current_object.input_param_values}
        current_input_points = {point.input_point_id: point for point in current_object.input_point_values}
        current_output_params = {param.output_param_id: param for param in current_object.output_param_values}

        # Обновляем значения аргументов
        self._update_argument_values(cursor, object_id, new_object.argument_values, current_args)

        # Обновляем значения входных параметров
        self._update_input_param_values(cursor, object_id, new_object.input_param_values, current_input_params)

        # Обновляем значения входных точек
        self._update_input_point_values(cursor, object_id, new_object.input_point_values, current_input_points)

        # Обновляем значения выходных параметров
        self._update_output_param_values(cursor, object_id, new_object.output_param_values, current_output_params)

    def _update_argument_values(self, cursor, object_id: int, new_args: List[ObjectArgumentValue], current_args: Dict):
        """Обновляет значения аргументов"""
        for new_arg in new_args:
            if new_arg.argument_id in current_args:
                # Обновляем существующую запись
                current_arg = current_args[new_arg.argument_id]
                cursor.execute('''
                    UPDATE value_to_argument 
                    SET argument_value = ?
                    WHERE id = ?
                ''', (new_arg.argument_value, current_arg.id))
                new_arg.id = current_arg.id
            else:
                # Добавляем новую запись
                cursor.execute('''
                    INSERT INTO value_to_argument (object_id, argument_id, argument_value)
                    VALUES (?, ?, ?)
                ''', (object_id, new_arg.argument_id, new_arg.argument_value))
                new_arg.id = cursor.lastrowid

        # Удаляем аргументы, которых больше нет
        new_arg_ids = {arg.argument_id for arg in new_args}
        for arg_id, current_arg in current_args.items():
            if arg_id not in new_arg_ids:
                cursor.execute('DELETE FROM value_to_argument WHERE id = ?', (current_arg.id,))

    def _update_input_param_values(self, cursor, object_id: int, new_params: List[ObjectInputParamValue],
                                   current_params: Dict):
        """Обновляет значения входных параметров"""
        for new_param in new_params:
            if new_param.input_param_id in current_params:
                # Обновляем существующую запись
                current_param = current_params[new_param.input_param_id]
                cursor.execute('''
                    UPDATE value_to_input_param 
                    SET parameter_id = ?
                    WHERE id = ?
                ''', (new_param.parameter_id, current_param.id))
                new_param.id = current_param.id
            else:
                # Добавляем новую запись
                cursor.execute('''
                    INSERT INTO value_to_input_param (object_id, input_param_id, parameter_id)
                    VALUES (?, ?, ?)
                ''', (object_id, new_param.input_param_id, new_param.parameter_id))
                new_param.id = cursor.lastrowid

        # Удаляем входные параметры, которых больше нет
        new_param_ids = {param.input_param_id for param in new_params}
        for param_id, current_param in current_params.items():
            if param_id not in new_param_ids:
                cursor.execute('DELETE FROM value_to_input_param WHERE id = ?', (current_param.id,))

    def _update_input_point_values(self, cursor, object_id: int, new_points: List[ObjectInputPointValue],
                                   current_points: Dict):
        """Обновляет значения входных точек"""
        for new_point in new_points:
            if new_point.input_point_id in current_points:
                # Обновляем существующую запись
                current_point = current_points[new_point.input_point_id]
                cursor.execute('''
                    UPDATE value_to_input_point 
                    SET point_id = ?
                    WHERE id = ?
                ''', (new_point.point_id, current_point.id))
                new_point.id = current_point.id
            else:
                # Добавляем новую запись
                cursor.execute('''
                    INSERT INTO value_to_input_point (object_id, input_point_id, point_id)
                    VALUES (?, ?, ?)
                ''', (object_id, new_point.input_point_id, new_point.point_id))
                new_point.id = cursor.lastrowid

        # Удаляем входные точки, которых больше нет
        new_point_ids = {point.input_point_id for point in new_points}
        for point_id, current_point in current_points.items():
            if point_id not in new_point_ids:
                cursor.execute('DELETE FROM value_to_input_point WHERE id = ?', (current_point.id,))

    def _update_output_param_values(self, cursor, object_id: int, new_outputs: List[ObjectOutputParamValue],
                                    current_outputs: Dict):
        """Обновляет значения выходных параметров"""
        for new_output in new_outputs:
            if new_output.output_param_id in current_outputs:
                # Обновляем существующую запись
                current_output = current_outputs[new_output.output_param_id]
                cursor.execute('''
                    UPDATE value_to_output_param 
                    SET parameter_id = ?
                    WHERE id = ?
                ''', (new_output.parameter_id, current_output.id))
                new_output.id = current_output.id
            else:
                # Добавляем новую запись
                cursor.execute('''
                    INSERT INTO value_to_output_param (object_id, output_param_id, parameter_id)
                    VALUES (?, ?, ?)
                ''', (object_id, new_output.output_param_id, new_output.parameter_id))
                new_output.id = cursor.lastrowid

        # Удаляем выходные параметры, которых больше нет
        new_output_ids = {param.output_param_id for param in new_outputs}
        for output_id, current_output in current_outputs.items():
            if output_id not in new_output_ids:
                cursor.execute('DELETE FROM value_to_output_param WHERE id = ?', (current_output.id,))
from CORE.db_dataclasses import *

import logging
from typing import List, Optional, Tuple

class ObjectRelationService:
    """
    Сервис для управления связями объектов с формами и треками.
    Обеспечивает операции по связыванию объектов с формами (HC_PC_object_to_form)
    и треками (object_to_track), а также методы для получения объектов по этим связям.
    Также содержит методы для загрузки полных данных объектов со всеми связанными значениями.
    """

    def __init__(self):
        pass

    def add_object_to_form(self, cursor, object_id: int, form_id: int):
        """Добавляет связь объекта с формой"""
        cursor.execute('''
            INSERT INTO HC_PC_object_to_form (form_id, object_id)
            VALUES (?, ?)
        ''', (form_id, object_id))

    def add_object_to_track(self, cursor, object_id: int, track_id: int, num_in_track: int):
        """Добавляет связь объекта с треком"""
        cursor.execute('''
            INSERT INTO object_to_track (track_id, object_id, num_in_track)
            VALUES (?, ?, ?)
        ''', (track_id, object_id, num_in_track))

    def get_objects_by_form(self, conn, form_id: int) -> List[BasePazzle]:
        """
        Получает все объекты связанные с формой
        """
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id 
            FROM object o
            JOIN HC_PC_object_to_form hc ON o.id = hc.object_id
            WHERE hc.form_id = ?
        ''', (form_id,))

        object_ids = [row['id'] for row in cursor.fetchall()]
        objects = []
        for obj_id in object_ids:
            obj = self._get_full_object(cursor, obj_id)
            if obj:
                objects.append(obj)

        return objects

    def get_objects_by_track(self, conn, track_id: int) -> List[Tuple[BasePazzle, int]]:
        """
        Получает все объекты в треке с их порядковыми номерами
        """
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, ott.num_in_track
            FROM object o
            JOIN object_to_track ott ON o.id = ott.object_id
            WHERE ott.track_id = ?
            ORDER BY ott.num_in_track
        ''', (track_id,))

        results = []
        for row in cursor.fetchall():
            obj = self._get_full_object(cursor, row['id'])
            if obj:
                results.append((obj, row['num_in_track']))

        return results

    def remove_object_from_form(self, cursor, object_id: int, form_id: int):
        """Удаляет связь объекта с формой"""
        cursor.execute('''
            DELETE FROM HC_PC_object_to_form 
            WHERE object_id = ? AND form_id = ?
        ''', (object_id, form_id))

    def remove_object_from_track(self, cursor, object_id: int, track_id: int):
        """Удаляет связь объекта с треком"""
        cursor.execute('''
            DELETE FROM object_to_track 
            WHERE object_id = ? AND track_id = ?
        ''', (object_id, track_id))

    def _get_full_object(self, cursor, object_id: int) -> Optional[BasePazzle]:
        """
        Получает полный объект BasePazzle со всеми связанными данными
        """
        # Получаем основной объект
        cursor.execute('''
            SELECT o.*, c.id as class_id, c.name as class_name, c.comment as class_comment, c.type as class_type
            FROM object o
            JOIN class c ON o.class_id = c.id
            WHERE o.id = ?
        ''', (object_id,))

        row = cursor.fetchone()
        if not row:
            return None

        # Создаем базовый объект
        class_ref = BaseClass(
            id=row['class_id'],
            name=row['class_name'],
            comment=row['class_comment'] or "",
            type=row['class_type']
        )

        base_pazzle = BasePazzle(
            id=row['id'],
            name=row['name'] or "",
            comment=row['comment'] or "",
            class_ref=class_ref
        )

        # Загружаем связанные данные
        self._load_related_data(cursor, object_id, base_pazzle)
        return base_pazzle

    def _load_related_data(self, cursor, object_id: int, base_pazzle: BasePazzle):
        """Загружает все связанные данные для объекта с обработкой NULL"""
        # Загружаем значения аргументов
        cursor.execute('''
            SELECT * FROM value_to_argument 
            WHERE object_id = ?
        ''', (object_id,))
        for row in cursor.fetchall():
            base_pazzle.argument_values.append(ObjectArgumentValue(
                id=row['id'],
                argument_id=row['argument_id'],
                argument_value=row['argument_value'] or ""
            ))

        # Загружаем значения входных параметров (обрабатываем NULL parameter_id)
        cursor.execute('''
            SELECT * FROM value_to_input_param 
            WHERE object_id = ?
        ''', (object_id,))
        for row in cursor.fetchall():
            base_pazzle.input_param_values.append(ObjectInputParamValue(
                id=row['id'],
                input_param_id=row['input_param_id'],
                parameter_id=row['parameter_id']  # Может быть NULL
            ))

        # Загружаем значения входных точек (обрабатываем NULL point_id)
        cursor.execute('''
            SELECT * FROM value_to_input_point 
            WHERE object_id = ?
        ''', (object_id,))
        for row in cursor.fetchall():
            base_pazzle.input_point_values.append(ObjectInputPointValue(
                id=row['id'],
                input_point_id=row['input_point_id'],
                point_id=row['point_id']  # Может быть NULL
            ))

        # Загружаем значения выходных параметров (обрабатываем NULL parameter_id)
        cursor.execute('''
            SELECT * FROM value_to_output_param 
            WHERE object_id = ?
        ''', (object_id,))
        for row in cursor.fetchall():
            base_pazzle.output_param_values.append(ObjectOutputParamValue(
                id=row['id'],
                output_param_id=row['output_param_id'],
                parameter_id=row['parameter_id']  # Может быть NULL
            ))
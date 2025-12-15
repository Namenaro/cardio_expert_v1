from CORE.db.db_manager import DBManager
from CORE.db_dataclasses import *

import sqlite3
from typing import List


class ClassesRepoRead:
    """Репозиторий для чтения классов из базы данных"""

    def __init__(self, db: DBManager):
        self.db = db

    def get_class_by_id(self, class_id: int) -> BaseClass:
        """Получает полную информацию о классе по ID"""
        with self.db.get_connection() as conn:
            # Получаем основную информацию о классе
            class_sql = "SELECT * FROM class WHERE id = ?"
            class_row = conn.execute(class_sql, (class_id,)).fetchone()

            if not class_row:
                raise ValueError(f"Класс с ID {class_id} не найден")

            # Создаем базовый объект класса
            base_class = BaseClass(
                name=class_row['name'],
                comment=class_row['comment'] or '',
                type=class_row['TYPE']
            )

            # Загружаем связанные данные
            base_class.constructor_arguments = self._get_constructor_arguments(conn, class_id)
            base_class.input_points = self._get_input_points(conn, class_id)
            base_class.input_params = self._get_input_params(conn, class_id)
            base_class.output_params = self._get_output_params(conn, class_id)

            base_class.id = class_id

            return base_class

    def _get_constructor_arguments(self, conn: sqlite3.Connection, class_id: int) -> List[ClassArgument]:
        """Получает аргументы конструктора для класса"""
        sql = "SELECT * FROM argument_to_class WHERE class_id = ? ORDER BY id"
        rows = conn.execute(sql, (class_id,)).fetchall()

        arguments = []
        for row in rows:
            arguments.append(ClassArgument(
                id=row['id'],
                name=row['name'],
                comment=row['comment'] or '',
                data_type=row['data_type'],
                default_value=row['default_value']
            ))
        return arguments

    def _get_input_points(self, conn: sqlite3.Connection, class_id: int) -> List[ClassInputPoint]:
        """Получает входные точки для класса"""
        sql = "SELECT * FROM input_point_to_class WHERE class_id = ? ORDER BY id"
        rows = conn.execute(sql, (class_id,)).fetchall()

        points = []
        for row in rows:
            points.append(ClassInputPoint(
                id=row['id'],
                name=row['name'],
                comment=row['comment'] or ''
            ))
        return points

    def _get_input_params(self, conn: sqlite3.Connection, class_id: int) -> List[ClassInputParam]:
        """Получает входные параметры для класса"""
        sql = "SELECT * FROM input_param_to_class WHERE class_id = ? ORDER BY id"
        rows = conn.execute(sql, (class_id,)).fetchall()

        params = []
        for row in rows:
            params.append(ClassInputParam(
                id=row['id'],
                name=row['name'],
                comment=row['comment'] or '',
                data_type=row['data_type']
            ))
        return params

    def _get_output_params(self, conn: sqlite3.Connection, class_id: int) -> List[ClassOutputParam]:
        """Получает выходные параметры для класса"""
        sql = "SELECT * FROM output_param_to_class WHERE class_id = ? ORDER BY id"
        rows = conn.execute(sql, (class_id,)).fetchall()

        params = []
        for row in rows:
            params.append(ClassOutputParam(
                id=row['id'],
                name=row['name'],
                comment=row['comment'] or '',
                data_type=row['data_type']
            ))
        return params

    def get_class_by_name(self, class_name: str) -> BaseClass:
        """Получает полную информацию о классе по имени"""
        with self.db.get_connection() as conn:
            class_sql = "SELECT id FROM class WHERE name = ?"
            class_row = conn.execute(class_sql, (class_name,)).fetchone()

            if not class_row:
                raise ValueError(f"Класс с именем '{class_name}' не найден")

            return self.get_class_by_id(class_row['id'])

    def get_all_classes(self, class_type: str = None) -> List[BaseClass]:
        """Получает все классы (опционально фильтруя по типу)"""
        with self.db.get_connection() as conn:
            if class_type:
                sql = "SELECT id FROM class WHERE TYPE = ? ORDER BY name"
                rows = conn.execute(sql, (class_type,)).fetchall()
            else:
                sql = "SELECT id FROM class ORDER BY name"
                rows = conn.execute(sql).fetchall()

            classes = []
            for row in rows:
                try:
                    class_info = self.get_class_by_id(row['id'])
                    classes.append(class_info)
                except Exception as e:
                    print(f"Ошибка при загрузке класса ID {row['id']}: {e}")

            return classes

    def get_classes_by_type(self) -> Dict[CLASS_TYPES, List[BaseClass]]:
        """Получает классы сгруппированные по типам CLASS_TYPES"""
        classes = self.get_all_classes()

        # Инициализируем словарь со всеми типами из enum
        grouped = {
            CLASS_TYPES.PC: [],
            CLASS_TYPES.HC: [],
            CLASS_TYPES.PS: [],
            CLASS_TYPES.SM: []
        }

        for class_info in classes:
            # Преобразуем строковый тип в enum
            try:
                class_type_enum = CLASS_TYPES(class_info.type)
                grouped[class_type_enum].append(class_info)
            except ValueError:
                # Если тип не соответствует ни одному значению enum, пропускаем
                print(f"Предупреждение: неизвестный тип класса '{class_info.type}' для класса '{class_info.name}'")

        return grouped

    def class_exists(self, class_id: int) -> bool:
        """Проверяет существование класса по ID"""
        with self.db.get_connection() as conn:
            sql = "SELECT 1 FROM class WHERE id = ?"
            row = conn.execute(sql, (class_id,)).fetchone()
            return row is not None

    def search_classes(self, search_term: str) -> List[BaseClass]:
        """Ищет классы по имени или комментарию"""
        with self.db.get_connection() as conn:
            sql = """
                SELECT id FROM class 
                WHERE name LIKE ? OR comment LIKE ?
                ORDER BY name
            """
            search_pattern = f"%{search_term}%"
            rows = conn.execute(sql, (search_pattern, search_pattern)).fetchall()

            classes = []
            for row in rows:
                try:
                    class_info = self.get_class_by_id(row['id'])
                    classes.append(class_info)
                except Exception as e:
                    print(f"Ошибка при загрузке класса ID {row['id']}: {e}")

            return classes

    def get_class_id_by_name(self, class_name: str) -> int:
        """Получает ID класса по имени"""
        with self.db.get_connection() as conn:
            sql = "SELECT id FROM class WHERE name = ?"
            row = conn.execute(sql, (class_name,)).fetchone()

            if not row:
                raise ValueError(f"Класс с именем '{class_name}' не найден")

            return row['id']

    def get_classes_by_specific_type(self, class_type: CLASS_TYPES) -> List[BaseClass]:
        """Получает классы определенного типа"""
        with self.db.get_connection() as conn:
            sql = "SELECT id FROM class WHERE TYPE = ? ORDER BY name"
            rows = conn.execute(sql, (class_type.value,)).fetchall()

            classes = []
            for row in rows:
                try:
                    class_info = self.get_class_by_id(row['id'])
                    classes.append(class_info)
                except Exception as e:
                    print(f"Ошибка при загрузке класса ID {row['id']}: {e}")

            return classes




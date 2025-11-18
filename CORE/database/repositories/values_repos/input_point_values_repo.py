import sqlite3
from typing import Optional, List
from CORE.database.repositories.base_repo import BaseRepo
from CORE.db_dataclasses import ObjectInputPointValue

class InputPointValuesRepo(BaseRepo):
    """Репозиторий для работы со значениями входных точек (value_to_input_point)"""

    def add_input_point_value(self, conn: sqlite3.Connection, object_id: int, value:ObjectInputPointValue) -> \
    Optional[int]:
        """Добавляет значение входной точки для объекта"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO value_to_input_point (object_id, input_point_id, point_id)
                VALUES (?, ?, ?)
            ''', (object_id, value.input_point_id, value.point_id))

            value_id = cursor.lastrowid
            conn.commit()
            return value_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении значения входной точки: {e}")
            conn.rollback()
            return None

    def get_input_point_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> List[ObjectInputPointValue]:
        """Получает все значения входных точек для объекта"""
        rows = self._execute_fetchall(conn,
                                      'SELECT id, object_id, input_point_id, point_id FROM value_to_input_point WHERE object_id = ?',
                                      (object_id,))

        return [
            ObjectInputPointValue(
                id=row['id'],
                object_id=row['object_id'],
                input_point_id=row['input_point_id'],
                point_id=row['point_id']
            )
            for row in rows
        ]

    def update_input_point_value(self, conn: sqlite3.Connection, value: ObjectInputPointValue) -> bool:
        """Обновляет значение входной точки"""
        if value.id is None:
            print("Ошибка: ID значения входной точки не указан")
            return False

        return self._execute_commit(conn,
                                    'UPDATE value_to_input_point SET point_id = ? WHERE id = ?',
                                    (value.point_id, value.id))

    def delete_input_point_value(self, conn: sqlite3.Connection, value_id: int) -> bool:
        """Удаляет значение входной точки по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_input_point WHERE id = ?',
                                    (value_id,))

    def delete_all_input_point_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Удаляет все значения входных точек для указанного объекта"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_input_point WHERE object_id = ?',
                                    (object_id,))
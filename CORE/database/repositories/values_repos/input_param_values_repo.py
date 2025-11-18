import sqlite3
from typing import Optional, List
from CORE.database.repositories.base_repo import BaseRepo
from CORE.db_dataclasses import ObjectInputParamValue


class InputParamValuesRepo(BaseRepo):
    """Репозиторий для работы со значениями входных параметров (value_to_input_param)"""

    def add_input_param_value(self, conn: sqlite3.Connection, object_id: int, value: ObjectInputParamValue) -> Optional[int]:
        """Добавляет значение входного параметра для объекта"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO value_to_input_param (object_id, input_param_id, parameter_id)
                VALUES (?, ?, ?)
            ''', (object_id, value.input_param_id, value.parameter_id))

            value_id = cursor.lastrowid
            conn.commit()
            return value_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении значения входного параметра: {e}")
            conn.rollback()
            return None

    def get_input_param_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> List[ObjectInputParamValue]:
        """Получает все значения входных параметров для объекта"""
        rows = self._execute_fetchall(conn,
                                      'SELECT id, object_id, input_param_id, parameter_id FROM value_to_input_param WHERE object_id = ?',
                                      (object_id,))

        return [
            ObjectInputParamValue(
                id=row['id'],
                object_id=row['object_id'],
                input_param_id=row['input_param_id'],
                parameter_id=row['parameter_id']
            )
            for row in rows
        ]

    def update_input_param_value(self, conn: sqlite3.Connection, value: ObjectInputParamValue) -> bool:
        """Обновляет значение входного параметра"""
        if value.id is None:
            print("Ошибка: ID значения входного параметра не указан")
            return False

        return self._execute_commit(conn,
                                    'UPDATE value_to_input_param SET parameter_id = ? WHERE id = ?',
                                    (value.parameter_id, value.id))

    def delete_input_param_value(self, conn: sqlite3.Connection, value_id: int) -> bool:
        """Удаляет значение входного параметра по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_input_param WHERE id = ?',
                                    (value_id,))

    def delete_all_input_param_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Удаляет все значения входных параметров для указанного объекта"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_input_param WHERE object_id = ?',
                                    (object_id,))
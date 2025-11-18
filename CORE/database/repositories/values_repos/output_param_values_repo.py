import sqlite3
from typing import Optional, List
from CORE.database.repositories.base_repo import BaseRepo
from CORE.db_dataclasses import ObjectOutputParamValue


class OutputParamValuesRepo(BaseRepo):
    """Репозиторий для работы со значениями выходных параметров (value_to_output_param)"""

    def add_output_param_value(self, conn: sqlite3.Connection, object_id: int, value:ObjectOutputParamValue) -> Optional[int]:
        """Добавляет значение выходного параметра для объекта"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO value_to_output_param (object_id, output_param_id, parameter_id)
                VALUES (?, ?, ?)
            ''', (object_id, value.output_param_id, value.parameter_id))

            value_id = cursor.lastrowid
            conn.commit()
            return value_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении значения выходного параметра: {e}")
            conn.rollback()
            return None

    def get_output_param_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> List[
        ObjectOutputParamValue]:
        """Получает все значения выходных параметров для объекта"""
        rows = self._execute_fetchall(conn,
                                      'SELECT id, object_id, output_param_id, parameter_id FROM value_to_output_param WHERE object_id = ?',
                                      (object_id,))

        return [
            ObjectOutputParamValue(
                id=row['id'],
                object_id=row['object_id'],
                output_param_id=row['output_param_id'],
                parameter_id=row['parameter_id']
            )
            for row in rows
        ]

    def update_output_param_value(self, conn: sqlite3.Connection, value: ObjectOutputParamValue) -> bool:
        """Обновляет значение выходного параметра"""
        if value.id is None:
            print("Ошибка: ID значения выходного параметра не указан")
            return False

        return self._execute_commit(conn,
                                    'UPDATE value_to_output_param SET parameter_id = ? WHERE id = ?',
                                    (value.parameter_id, value.id))

    def delete_output_param_value(self, conn: sqlite3.Connection, value_id: int) -> bool:
        """Удаляет значение выходного параметра по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_output_param WHERE id = ?',
                                    (value_id,))

    def delete_all_output_param_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Удаляет все значения выходных параметров для указанного объекта"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_output_param WHERE object_id = ?',
                                    (object_id,))
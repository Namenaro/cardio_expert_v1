import sqlite3
from typing import Optional, List
from CORE.database.repositories.objects_repos.base_repo import BaseRepo
from CORE.db_dataclasses import ObjectArgumentValue


class ArgumentValuesRepo(BaseRepo):
    """Репозиторий для работы со значениями аргументов (value_to_argument)"""

    def add_argument_value(self, conn: sqlite3.Connection, object_id: int, argument_id: int, value: str) -> Optional[
        int]:
        """Добавляет значение аргумента для объекта"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO value_to_argument (object_id, argument_id, argument_value)
                VALUES (?, ?, ?)
            ''', (object_id, argument_id, value))

            value_id = cursor.lastrowid
            conn.commit()
            return value_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении значения аргумента: {e}")
            conn.rollback()
            return None

    def get_argument_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> List[ObjectArgumentValue]:
        """Получает все значения аргументов для объекта"""
        rows = self._execute_fetchall(conn,
                                      'SELECT id, object_id, argument_id, argument_value FROM value_to_argument WHERE object_id = ?',
                                      (object_id,))

        return [
            ObjectArgumentValue(
                id=row['id'],
                object_id=row['object_id'],
                argument_id=row['argument_id'],
                argument_value=row['argument_value']
            )
            for row in rows
        ]

    def update_argument_value(self, conn: sqlite3.Connection, value: ObjectArgumentValue) -> bool:
        """Обновляет значение аргумента"""
        if value.id is None:
            print("Ошибка: ID значения аргумента не указан")
            return False

        return self._execute_commit(conn,
                                    'UPDATE value_to_argument SET argument_value = ? WHERE id = ?',
                                    (value.argument_value, value.id))

    def delete_argument_value(self, conn: sqlite3.Connection, value_id: int) -> bool:
        """Удаляет значение аргумента по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_argument WHERE id = ?',
                                    (value_id,))

    def delete_all_argument_values_by_object(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Удаляет все значения аргументов для указанного объекта"""
        return self._execute_commit(conn,
                                    'DELETE FROM value_to_argument WHERE object_id = ?',
                                    (object_id,))
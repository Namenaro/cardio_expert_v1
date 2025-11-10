import sqlite3
from typing import Optional, List
from CORE.database.repositories.objects_helpers_repos.base_repo import BaseRepo
from CORE.db_dataclasses import *


class ObjectsRepo(BaseRepo):
    """Репозиторий для работы с объектами (таблица object)"""

    def add_object(self, conn: sqlite3.Connection, class_id: int, name: Optional[str], comment: str = "") -> Optional[int]:
        """Добавляет новый объект"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO object (class_id, name, comment)
                VALUES (?, ?, ?)
            ''', (class_id, name, comment))

            object_id = cursor.lastrowid
            conn.commit()
            return object_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении объекта: {e}")
            conn.rollback()
            return None

    def get_object_by_id(self, conn: sqlite3.Connection, object_id: int) -> Optional[BasePazzle]:
        """Получает объект по ID"""
        row = self._execute_fetchone(conn,
                                     'SELECT id, class_id, name, comment FROM object WHERE id = ?',
                                     (object_id,))

        if row:
            return BasePazzle(
                id=row['id'],
                name=row['name'],
                comment=row['comment']
            )
        return None



    def update_object(self, conn: sqlite3.Connection, obj: BasePazzle) -> bool:
        """Обновляет объект"""
        if obj.id is None:
            print("Ошибка: ID объекта не указан")
            return False

        return self._execute_commit(conn,
                                    'UPDATE object SET name = ?, comment = ? WHERE id = ?',
                                    (obj.name, obj.comment, obj.id))

    def delete_object(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Удаляет объект по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM object WHERE id = ?',
                                    (object_id,))
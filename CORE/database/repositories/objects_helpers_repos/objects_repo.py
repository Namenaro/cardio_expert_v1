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

    def add_object_to_form(self, conn: sqlite3.Connection, form_id: int, object_id: int) -> Optional[int]:
        """Добавляет связь объекта с формой"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO HC_PC_object_to_form (form_id, object_id)
                VALUES (?, ?)
            ''', (form_id, object_id))

            relation_id = cursor.lastrowid
            conn.commit()
            return relation_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении связи объекта с формой: {e}")
            conn.rollback()
            return None

    def get_objects_by_form(self, conn: sqlite3.Connection, form_id: int) -> List[int]:
        """Получает список ID объектов, связанных с формой"""
        rows = self._execute_fetchall(conn,
                                      'SELECT object_id FROM HC_PC_object_to_form WHERE form_id = ? ORDER BY id',
                                      (form_id,))

        return [row['object_id'] for row in rows]

    def get_forms_by_object(self, conn: sqlite3.Connection, object_id: int) -> List[int]:
        """Получает список ID форм, связанных с объектом"""
        rows = self._execute_fetchall(conn,
                                      'SELECT form_id FROM HC_PC_object_to_form WHERE object_id = ? ORDER BY id',
                                      (object_id,))

        return [row['form_id'] for row in rows]

    def delete_object_from_form(self, conn: sqlite3.Connection, form_id: int, object_id: int) -> bool:
        """Удаляет связь объекта с формой"""
        return self._execute_commit(conn,
                                    'DELETE FROM HC_PC_object_to_form WHERE form_id = ? AND object_id = ?',
                                    (form_id, object_id))

    def delete_all_objects_from_form(self, conn: sqlite3.Connection, form_id: int) -> bool:
        """Удаляет все связи объектов с указанной формой"""
        return self._execute_commit(conn,
                                    'DELETE FROM HC_PC_object_to_form WHERE form_id = ?',
                                    (form_id,))

    def delete_all_forms_from_object(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Удаляет все связи форм с указанным объектом"""
        return self._execute_commit(conn,
                                    'DELETE FROM HC_PC_object_to_form WHERE object_id = ?',
                                    (object_id,))

    def relation_exists(self, conn: sqlite3.Connection, form_id: int, object_id: int) -> bool:
        """Проверяет существование связи"""
        row = self._execute_fetchone(conn,
                                     'SELECT 1 FROM HC_PC_object_to_form WHERE form_id = ? AND object_id = ?',
                                     (form_id, object_id))

        return row is not None
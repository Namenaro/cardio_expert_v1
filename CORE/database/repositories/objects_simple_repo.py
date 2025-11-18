import sqlite3
from CORE.database.repositories.base_repo import BaseRepo
from CORE.db_dataclasses import *


class ObjectsSimpleRepo(BaseRepo):
    """Репозиторий для работы с объектами (таблица object)"""

    def add_object_entry(self, conn: sqlite3.Connection, object:BasePazzle) -> Optional[int]:
        """Добавляет новый объект"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO object (class_id, name, comment)
                VALUES (?, ?, ?)
            ''', (object.class_ref.id, object.name, object.comment))

            object_id = cursor.lastrowid
            conn.commit()
            return object_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении объекта: {e}")
            conn.rollback()
            return None

    def get_object_entry_by_id(self, conn: sqlite3.Connection, object_id: int) -> BasePazzle:
        """Получает объект по ID

           Args:
               conn: SQLite соединение
               object_id: ID объекта

           Returns:
               BasePazzle: найденный объект

           Raises:
               ValueError: если объект не найден
               sqlite3.Error: при ошибках базы данных
           """
        row = self._execute_fetchone(conn,
                                     'SELECT id, class_id, name, comment FROM object WHERE id = ?',
                                     (object_id,))

        if row:
            return BasePazzle(
                id=row['id'],
                name=row['name'],
                comment=row['comment']
            )
        raise ValueError(f"Объект с ID {object_id} не найден")


    def update_object_entry(self, conn: sqlite3.Connection, obj: BasePazzle) -> bool:
        """Обновляет объект"""
        if obj.id is None:
            print("Ошибка: ID объекта не указан")
            return False

        return self._execute_commit(conn,
                                    'UPDATE object SET name = ?, comment = ?, class_id =? WHERE id = ?',
                                    (obj.name, obj.comment, obj.class_ref.id, obj.id))

    def delete_object(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Удаляет объект по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM object WHERE id = ?',
                                    (object_id,))

    def connect_object_to_form(self, conn: sqlite3.Connection, form_id: int, object_id: int) -> Optional[int]:
        """Добавляет связь объекта с формой"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO HC_PC_object_to_form (form_id, object_id)
                VALUES (?, ?)
            ''', (form_id, object_id))

            relation_id = cursor.lastrowid
            return relation_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении связи объекта с формой: {e}")
            raise


    def get_objects_ids_by_form(self, conn: sqlite3.Connection, form_id: int) -> List[int]:
        """Получает список ID объектов, связанных с формой"""
        rows = self._execute_fetchall(conn,
                                      'SELECT object_id FROM HC_PC_object_to_form WHERE form_id = ? ORDER BY id',
                                      (form_id,))

        return [row['object_id'] for row in rows]


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



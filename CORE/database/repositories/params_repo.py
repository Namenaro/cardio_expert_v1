from CORE.db_dataclasses import Parameter

import sqlite3
from typing import List, Optional


class ParamsRepo:

    def add_new_parameter(self, conn: sqlite3.Connection, form_id: int, parameter: Parameter) -> Optional[int]:
        """
        Добавляет новый параметр для указанной формы
        Возвращает ID созданного параметра или None в случае ошибки
        """
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO parameter (name, form_id, comment, data_type)
                VALUES (?, ?, ?, ?)
            ''', (parameter.name, form_id, parameter.comment, parameter.data_type))

            param_id = cursor.lastrowid
            conn.commit()
            return param_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении параметра: {e}")
            raise

    def delete_parameter_by_id(self, conn: sqlite3.Connection, parameter_id: int) -> bool:
        """
        Удаляет параметр по его ID
        Возвращает True если удаление успешно, False в случае ошибки
        """
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM parameter WHERE id = ?', (parameter_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении параметра: {e}")
            raise

    def read_all_parameters_by_form_id(self, conn: sqlite3.Connection, form_id: int) -> List[Parameter]:
        """
        Возвращает список всех параметров для указанной формы
        """
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, comment, data_type 
                FROM parameter 
                WHERE form_id = ?
                ORDER BY id
            ''', (form_id,))

            parameters = []
            for row in cursor.fetchall():
                parameter = Parameter(
                    id=row[0],
                    name=row[1],
                    comment=row[2],
                    data_type=row[3]
                )
                parameters.append(parameter)

            return parameters
        except sqlite3.Error as e:
            print(f"Ошибка при чтении параметров: {e}")
            raise

    def update_parameter(self, conn: sqlite3.Connection, parameter: Parameter) -> bool:
        """
        Обновляет данные параметра
        Возвращает True если обновление успешно, False в случае ошибки
        """
        if parameter.id is None:
            print("Ошибка: ID параметра не указан")
            return False

        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE parameter 
                SET name = ?, comment = ?, data_type = ?
                WHERE id = ?
            ''', (parameter.name, parameter.comment, parameter.data_type, parameter.id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении параметра: {e}")
            raise

    def delete_all_parameters_of_form(self, conn: sqlite3.Connection, form_id: int) -> bool:
        """
        Удаляет все параметры указанной формы
        Возвращает True если удаление успешно, False в случае ошибки
        """
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM parameter WHERE form_id = ?', (form_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении всех параметров формы: {e}")
            raise


from CORE.db_dataclasses import Form

import sqlite3
from typing import List, Optional


class FormsSimpleRepo:

    def get_all_forms(self, conn: sqlite3.Connection) -> List[Form]:
        """
        Возвращает список всех форм
        """
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, comment, path_to_pic, path_to_dataset 
                FROM form 
                ORDER BY id
            ''')

            forms = []
            for row in cursor.fetchall():
                form = Form(
                    id=row['id'],
                    name=row['name'],
                    comment=row['comment'],
                    path_to_pic=row['path_to_pic'],
                    path_to_dataset=row['path_to_dataset']
                )
                forms.append(form)

            return forms
        except sqlite3.Error as e:
            print(f"Ошибка при получении всех форм: {e}")
            raise

    def delete_form_by_id(self, conn: sqlite3.Connection, form_id: int) -> bool:
        """
        Удаляет форму по её ID
        Возвращает True если удаление успешно, False в случае ошибки
        """
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM form WHERE id = ?', (form_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при удалении формы: {e}")
            raise

    def get_form_by_id(self, conn: sqlite3.Connection, form_id: int) -> Optional[Form]:
        """
        Получает форму по её ID
        Возвращает объект Form или None если форма не найдена
        """
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, comment, path_to_pic, path_to_dataset 
                FROM form 
                WHERE id = ?
            ''', (form_id,))

            row = cursor.fetchone()
            if row:
                return Form(
                    id=row['id'],
                    name=row['name'],
                    comment=row['comment'],
                    path_to_pic=row['path_to_pic'],
                    path_to_dataset=row['path_to_dataset']
                )
            return None
        except sqlite3.Error as e:
            print(f"Ошибка при получении формы по ID: {e}")
            raise

    def update_form(self, conn: sqlite3.Connection, form: Form) -> bool:
        """
        Обновляет данные формы
        Возвращает True если обновление успешно, False в случае ошибки
        """
        if form.id is None:
            print("Ошибка: ID формы не указан")
            return False

        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE form 
                SET name = ?, comment = ?, path_to_pic = ?, path_to_dataset = ?
                WHERE id = ?
            ''', (form.name, form.comment, form.path_to_pic, form.path_to_dataset, form.id))

            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении формы: {e}")
            raise

    def add_form(self, conn: sqlite3.Connection, form: Form) -> Optional[int]:
        """
        Добавляет новую форму
        Возвращает ID созданной формы или None в случае ошибки
        """
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO form (name, comment, path_to_pic, path_to_dataset)
                VALUES (?, ?, ?, ?)
            ''', (form.name, form.comment, form.path_to_pic, form.path_to_dataset))

            form_id = cursor.lastrowid
            conn.commit()
            return form_id
        except sqlite3.IntegrityError as e:
            print(f"Ошибка целостности при добавлении формы (возможно, имя уже существует): {e}")
            raise
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении формы: {e}")
            raise

    def get_forms_with_search(self, conn: sqlite3.Connection, search_term: str) -> List[Form]:
        """
        Ищет формы по имени или комментарию
        """
        try:
            cursor = conn.cursor()
            search_pattern = f'%{search_term}%'
            cursor.execute('''
                SELECT id, name, comment, path_to_pic, path_to_dataset 
                FROM form 
                WHERE name LIKE ? OR comment LIKE ?
                ORDER BY id
            ''', (search_pattern, search_pattern))

            forms = []
            for row in cursor.fetchall():
                form = Form(
                    id=row['id'],
                    name=row['name'],
                    comment=row['comment'],
                    path_to_pic=row['path_to_pic'],
                    path_to_dataset=row['path_to_dataset']
                )
                forms.append(form)

            return forms
        except sqlite3.Error as e:
            print(f"Ошибка при поиске форм: {e}")
            raise
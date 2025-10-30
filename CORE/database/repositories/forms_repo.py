from CORE.dataclasses import Form, Track, Point, SM_Class, PS_Class, PC_Class, HC_Class, Parameter, SM_Object, PS_Object
from CORE.database.connection import DatabaseConnection
from CORE.database.schema import Schema

import sqlite3
from typing import List, Optional, Dict

class FormsRepo:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_forms_summaries(self) -> List[Form]:
        """Вернуть список всех форм"""
        try:
            conn = self.db.get_connection()


            cursor = conn.cursor()
            cursor.execute('''
                    SELECT id, name, comment, path_to_pic, path_to_dataset 
                    FROM form
            ''')

            return [
                    Form(id=row[0], name=row[1], comment=row[2],
                         path_to_pic=row[3], path_to_dataset=row[4])
                    for row in cursor.fetchall()
            ]

        except Exception as e:
            print(f"Ошибка при получении списка форм: {e}")
            return []

    def get_form(self, form_id: int) -> Optional[Form]:
        """Загрузка формы по ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Загрузка основной информации о форме
            cursor.execute('SELECT id, name, comment, path_to_pic, path_to_dataset FROM form WHERE id = ?', (form_id,))
            form_data = cursor.fetchone()

            if not form_data:
                return None

            form = Form(
                id=form_data[0],
                name=form_data[1],
                comment=form_data[2],
                path_to_pic=form_data[3],
                path_to_dataset = form_data[4]
            )

            # Загрузка точек формы
            # Загрузка параметров формы
            # Загрузка шагов формы
            # Загрузка измерителей параметров
            # Загрузка жестких условий
            return form

    def delete_form(self, form_id: int):
        """Удаление формы по ID"""
        pass

    def add_new_form(self, form: Form) -> Optional[int]:
        """Сохранение формы в базу данных и возврат ID новой записи"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        try:
            # Основная информация о форме:
            cursor.execute('''
                INSERT INTO form (name, comment, path_to_pic, path_to_dataset)
                VALUES (?, ?, ?, ?)
            ''', (form.name, form.comment, form.path_to_pic, form.path_to_dataset))

            new_id = cursor.lastrowid
            conn.commit()
            return new_id

        except Exception as e:
            print(f"Ошибка при добавлении формы: {e}")
            return None

if __name__ == "__main__":
    schema = Schema()

    if schema.db_exists():
        schema.delete_database()
    schema.create_tables()
    repo = FormsRepo()

    test_form = Form(name="test_form",
                     comment="комментарий",
                     path_to_pic="\путь к картике",
                     path_to_dataset="\путь к датасету")

    test_form.points.append(Point(name="point1", comment="коммент"))
    test_form.points.append(Point(name="point2", comment="коммент"))

    test_form.parameters.append(Parameter(name="param1", comment="коммент"))
    test_form.parameters.append(Parameter(name="param2", comment="коммент"))

    track = Track()


    id = repo.add_new_form(test_form)
    print(id)




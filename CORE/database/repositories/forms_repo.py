from CORE.dataclasses import Form, Point, SM_Class, PS_Class, PC_Class, HC_Class
from CORE.database.connection import DatabaseConnection

import sqlite3
from typing import List, Optional, Dict

class DBWrapperForDoctor:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_forms_names(self)->Dict[int, str]:
        """ Вернуть список всех ID форм c их именами, т.е. dict{form.id, form.name}"""
        pass

    def load_form(self, form_id: int) -> Optional[Form]:
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

    def save_form(self, form:Form):
        """Сохранение формы в базу данных"""
        pass


from CORE.db_dataclasses import Form, Track, Point, SM_Class, PS_Class, PC_Class, HC_Class, Parameter, SM_Object, PS_Object
from CORE.database.db_manager import DBManager

from CORE.database.repositories.points_repo import PointsRepo


import sqlite3
from sqlite3 import Cursor


from typing import List, Optional, Dict
import logging

class FormsReadRepo:
    def __init__(self, db: DBManager) -> None:
        """Инициализация репозитория"""
        self.db = db
        self._points_repo = PointsRepo()

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
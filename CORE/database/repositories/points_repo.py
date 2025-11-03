from CORE.dataclasses import Form, Track, Point, SM_Class, PS_Class, PC_Class, HC_Class, Parameter, SM_Object, PS_Object
from CORE.database.db_manager import DBManager


import sqlite3
from typing import List, Optional, Dict

class PointsRepo:
    def __init__(self, db: DBManager) -> None:
        """Инициализация репозитория"""
        self.db = db

    def get_point_by_id(self, point_id:int)->Optional[Point]:
        pass

    def delete_point(self, point_id:int)->bool:
        pass

    def get_points_by_form_id(self)->List[Point]:
        pass

    def add_new_point(self, point:Point, form_id:int)-> Optional[int]:
        """
            Добавляет новую точку в базу данных.
            """
        try:
            with self.db.get_connection() as conn:
                cursor= conn.cursor()
                query = """
                        INSERT INTO point (name, comment, form_id)
                        VALUES (?, ?, ?)
                    """
                cursor.execute(query, (point.name, point.comment, form_id))
                conn.commit()
                return cursor.lastrowid

        except Exception as e:
            conn.rollback()
            print(f"Ошибка при добавлении точки: {e}")
            return None




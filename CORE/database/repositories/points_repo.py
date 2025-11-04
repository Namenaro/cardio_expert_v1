from CORE.db_dataclasses import Form, Track, Point, SM_Class, PS_Class, PC_Class, HC_Class, Parameter, SM_Object, PS_Object
from CORE.database.db_manager import DBManager

import sqlite3
from typing import List, Optional, Dict

class PointsRepo:
    """ Работа с точками формы (чтение и запись), работает только через переданное соединение"""

    def add_new_point(self, conn: sqlite3.Connection, form_id: int, point: Point)-> Optional[int]:
        """
        Добавляет одну новую точку к форме.
        Возвращает ID созданной точки или None при ошибке.
        """
        cursor = conn.cursor()
        try:

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






from CORE.dataclasses import Form, Track, Point, SM_Class, PS_Class, PC_Class, HC_Class, Parameter, SM_Object, PS_Object
from CORE.database.connection import DatabaseConnection
from CORE.database.schema import Schema

import sqlite3
from typing import List, Optional, Dict

class PointsRepo:
    def __init__(self, db: DatabaseConnection) -> None:
        """Инициализация репозитория"""
        self.db = db

    def get_point_by_id(self, point_id:int)->Optional[Point]:
        pass

    def delete_point(self, point_id:int)->bool:
        pass

    def get_points_by_form_id(self)->List[Point]:
        pass

    def add_new_point(self, point:Point, form_id:int)-> Optional[int]:
        pass




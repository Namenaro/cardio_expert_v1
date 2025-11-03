from CORE.db_dataclasses import Form, Track, Point, SM_Class, PS_Class, PC_Class, HC_Class, Parameter, SM_Object, PS_Object
from CORE.database.connection import DatabaseConnection
from CORE.database.schema import Schema

import sqlite3
from typing import List, Optional, Dict, Any

class PS_ObjectsRepo:
    def __init__(self, db: DatabaseConnection) -> None:
        """Инициализация репозитория"""
        self.db = db

    def add_new(self, ps_object:PS_Object)->Optional[int]:
        pass


    def delete_obj(self, ps_obj_id)->bool:
        pass

    def get_obj_by_id(self, ps_obj_id)->Optional[PS_Object]:
        pass

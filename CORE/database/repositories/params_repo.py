from CORE.db_dataclasses import Form, Track, Point, SM_Class, PS_Class, PC_Class, HC_Class, Parameter, SM_Object, PS_Object
from CORE.database.db_manager import DBManager


import sqlite3
from typing import List, Optional, Dict

class ParamsRepo:
    def __init__(self, db: DBManager) -> None:
        """Инициализация репозитория"""
        self.db = db

    def get_param_by_id(self, point_id:int)->Optional[Parameter]:
        pass

    def delete_param(self, point_id:int)->bool:
        pass

    def get_params_by_form_id(self)->List[Parameter]:
        pass

    def add_new_param(self, param:Parameter, form_id:int)-> Optional[int]:
        pass


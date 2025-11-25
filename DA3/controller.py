
from CORE.db.forms_services import FormService, PointService, ParameterService, StepService, TrackService, \
    ObjectsService
from CORE.db_dataclasses import *

from CORE.db.db_manager import DBManager
from CORE.settings import DB_PATH

from PySide6.QtWidgets import QMessageBox
from typing import List, Optional


class Contoller:
    def __init__(self, db_path:str=DB_PATH):
        self.db_manager = DBManager(db_path)

        self.form_service = FormService()
        self.point_service = PointService()
        self.parameter_service = ParameterService()
        self.objects_service = ObjectsService()
        self.track_service = TrackService()
        self.step_service = StepService()

    def get_all_forms_summaries(self)-> List[Form]:
        with self.db_manager.get_connection() as conn:
            forms = self.form_service.get_all_forms(conn)
            return forms



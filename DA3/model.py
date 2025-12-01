
from CORE.db.forms_services import FormService, PointService, ParameterService, StepService, TrackService, \
    ObjectsService
from CORE.db_dataclasses import *

from CORE.db.db_manager import DBManager
from CORE.settings import DB_PATH


from typing import List, Optional, Union



class Model:
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


    def get_form_by_id(self, from_id):
        with self.db_manager.get_connection() as conn:
            form = self.form_service.get_form_by_id(form_id=from_id, conn=conn)
            return form


    def add_object(self, obj):
        pass

    def update_object(self, obj):
        pass

    def delete_object(self, obj: Union[Point, Parameter, Step, BasePazzle, Form, Track]) -> bool:
        """
        Удаление объекта из базы данных

        Args:
            obj: объект для удаления (Point, Parameter, Step, BasePazzle или Form)

        Returns:
            True если удаление успешно, False если нет
        """
        if obj.id is None:
            raise ValueError(" Нельзя удалять объект без id")
        with self.db_manager.get_connection() as conn:
            if isinstance(obj, Point):
                return self.point_service.delete_point(conn=conn,point_id=obj.id)
            elif isinstance(obj, Parameter):
                return self.parameter_service.delete_parameter(conn=conn,parameter_id=obj.id)
            elif isinstance(obj, Step):
                return self.step_service.delete_step(conn=conn, step_id=obj.id)
            elif isinstance(obj, BasePazzle):
                return self.objects_service.delete_object(conn=conn, object_id=obj.id)
            elif isinstance(obj, Form):
                return self.form_service.delete_form(conn=conn, form_id=obj.id)
            elif isinstance(obj, Track):
                return self.track_service.delete_track(conn=conn, track_id=obj.id)
            else:
                raise ValueError(f"Неизвестный тип объекта пытаемся удалить: {type(obj)}")






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

    # ================= ГЕТТЕРЫ ======================
    def get_all_forms_summaries(self)-> List[Form]:
        with self.db_manager.get_connection() as conn:
            forms = self.form_service.get_all_forms(conn)
            return forms

    def get_form_by_id(self, form_id):
        with self.db_manager.get_connection() as conn:
            form = self.form_service.get_form_by_id(form_id=form_id, conn=conn)
            return form

    # ================= ДОБАВЛЕНИЕ ======================
    def add_SM(self, num_in_track:int, obj:BasePazzle, track_id):
        with self.db_manager.get_connection() as conn:
            track = self.track_service.get_track_by_id(conn=conn, track_id=track_id)
            track.insert_sm(sm=obj, num_in_track=num_in_track)
            track = self.track_service.update_track(conn=conn, track=track)
            return track.SMs[num_in_track]

    def add_PC(self, obj:BasePazzle, form_id:int)->BasePazzle:
        with self.db_manager.get_connection() as conn:
            return self.objects_service.add_object(conn=conn, base_pazzle=obj, form_id=form_id)

    def add_HC(self, obj:BasePazzle, form_id:int)->BasePazzle:
        with self.db_manager.get_connection() as conn:
            return self.objects_service.add_object(conn=conn, base_pazzle=obj, form_id=form_id)

    def add_PS(self, obj:BasePazzle, track_id:int):
        with self.db_manager.get_connection() as conn:
            return self.objects_service.add_object(conn=conn, base_pazzle=obj, track_id=track_id)

    def add_track(self, track:Track, step_id:int)->Track:
        with self.db_manager.get_connection() as conn:
            return self.track_service.add_track(conn=conn, track=track, step_id=step_id)

    def add_point(self, point:Point, form_id:int)->Point:
        with self.db_manager.get_connection() as conn:
            return self.point_service.add_point(conn=conn, point=point, form_id=form_id)

    def add_parameter(self, parameter:Parameter, form_id:int)->Parameter:
        with self.db_manager.get_connection() as conn:
            return self.parameter_service.add_parameter(conn=conn, parameter=parameter, form_id=form_id)

    def add_step(self, step:Step, form_id:int)->Step:
        with self.db_manager.get_connection() as conn:
            # Проверка корректности индекса
            form = self.form_service.get_form_by_id(form_id=form_id, conn=conn)
            if step.num_in_form < 0 or step.num_in_form > len(form.steps):
                raise ValueError(f"Номер шага, вставляемого в форму, некорректный: {step.num_in_form}")

            # Изменим нумерацию шагов, следующих после вставляемого: номера их всех сдвигаем на один вправо
            for old_step in form.steps:
                if old_step.num_in_form>=step.num_in_form:
                    old_step.num_in_form+=1
                    self.step_service.update_step(conn=conn, step=step)
            # Добавим новый шаг
            return self.step_service.add_step(conn=conn, step=step, form_id=form_id)

    def add_form(self, form:Form)->Form:
        with self.db_manager.get_connection() as conn:
            return  self.form_service.add_form(conn=conn, form=form)

    # ================= ОБНОВЛЕНИЕ ======================
    def update_main_info(self, form:Form)->Form:
        with self.db_manager.get_connection() as conn:
            return self.form_service.update_form_main_info(conn, form=form)

    def update_object(self, obj: Union[Point, Parameter, Step, BasePazzle, Track])->Union[Point, Parameter, Step, BasePazzle, Track]:
        """
        Обновление объекта в базе данных (любые подобъекты формы, но не она сама)
        :param obj: объект для обновления
        :return: этот же объект, но со всеми заполненными id
        """
        if obj.id is None:
            raise ValueError(" Нельзя обновить объект без id")
        with self.db_manager.get_connection() as conn:
            if isinstance(obj, Point):
                return self.point_service.update_point(conn=conn, point=obj)
            elif isinstance(obj, Parameter):
                return self.parameter_service.update_parameter(conn=conn, parameter=obj)
            elif isinstance(obj, Step):
                return self.step_service.update_step(conn=conn, step=obj)
            elif isinstance(obj, BasePazzle):
                return self.objects_service.update_object(conn=conn,base_pazzle=obj)
            elif isinstance(obj, Track):
                return self.track_service.update_track(conn=conn, track=obj)
            else:
                raise ValueError(f"Неизвестный тип объекта пытаемся обновить: {type(obj)}")

    # ================= УДАЛЕНИЕ ======================
    def delete_object(self, obj: Union[Point, Parameter, Step, BasePazzle, Form, Track]) -> bool:
        """
        Удаление объекта из базы данных
        :param obj: объект для удаления (Point, Parameter, Step, BasePazzle или Form)
        :return: True если удаление успешно, False если нет
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





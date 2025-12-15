
from CORE.db.forms_services import FormService, PointService, ParameterService, StepService, TrackService, \
    ObjectsService

from CORE.db.classes_service import ClassesRepoRead
from CORE.db_dataclasses import *

from CORE.db.db_manager import DBManager
from CORE.settings import DB_PATH


from typing import List, Optional, Union, Tuple



class Model:
    def __init__(self, db_path:str=DB_PATH):
        self.db_manager = DBManager(db_path)

        self.form_service = FormService()
        self.point_service = PointService()
        self.parameter_service = ParameterService()
        self.objects_service = ObjectsService()
        self.track_service = TrackService()
        self.step_service = StepService()

        self.classes_service = ClassesRepoRead(self.db_manager)

    # ================= ГЕТТЕРЫ ======================
    def get_all_forms_summaries(self)-> List[Form]:
        with self.db_manager.get_connection() as conn:
            forms = self.form_service.get_all_forms(conn)
            return forms

    def get_form_by_id(self, form_id)->Form:
        with self.db_manager.get_connection() as conn:
            form = self.form_service.get_form_by_id(form_id=form_id, conn=conn)
            return form

    def get_HCs_classes(self):
        hc_classes = self.classes_service.get_classes_by_specific_type(CLASS_TYPES.HC)
        return hc_classes

    def get_PCs_classes(self):
        return self.classes_service.get_classes_by_specific_type(CLASS_TYPES.PC)

    def get_SMs_classes(self):
        return self.classes_service.get_classes_by_specific_type(CLASS_TYPES.SM)

    def get_PSs_classes(self):
        return self.classes_service.get_classes_by_specific_type(CLASS_TYPES.PS)


    # ================= ДОБАВЛЕНИЕ ======================
    def add_SM(self, num_in_track: int, obj: BasePazzle, track_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                track = self.track_service.get_track_by_id(conn=conn, track_id=track_id)
                track.insert_sm(sm=obj, num_in_track=num_in_track)
                self.track_service.update_track(conn=conn, track=track)
                return True, "SM успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления SM: {str(e)}"

    def add_PC(self, obj: BasePazzle, form_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.objects_service.add_object(conn=conn, base_pazzle=obj, form_id=form_id)
                return True, "PC успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления PC: {str(e)}"

    def add_HC(self, obj: BasePazzle, form_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.objects_service.add_object(conn=conn, base_pazzle=obj, form_id=form_id)
                return True, "HC успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления HC: {str(e)}"

    def add_PS(self, obj: BasePazzle, track_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.objects_service.add_object(conn=conn, base_pazzle=obj, track_id=track_id)
                return True, "PS успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления PS: {str(e)}"

    def add_track(self, track: Track, step_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.track_service.add_track(conn=conn, track=track, step_id=step_id)
                return True, "Трек успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления трека: {str(e)}"

    def add_point(self, point: Point, form_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.point_service.add_point(conn=conn, point=point, form_id=form_id)
                return True, "Точка успешно добавлена"
        except Exception as e:
            return False, f"Ошибка добавления точки: {str(e)}"

    def add_parameter(self, parameter: Parameter, form_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.parameter_service.add_parameter(conn=conn, parameter=parameter, form_id=form_id)
                return True, "Параметр успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления параметра: {str(e)}"

    def add_step(self, step: Step, form_id: int) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                # Проверка корректности индекса
                form = self.form_service.get_form_by_id(form_id=form_id, conn=conn)
                if step.num_in_form < 0 or step.num_in_form > len(form.steps):
                    return False, f"Некорректный номер шага: {step.num_in_form}"

                # Изменим нумерацию шагов, следующих после вставляемого
                for old_step in form.steps:
                    if old_step.num_in_form >= step.num_in_form:
                        old_step.num_in_form += 1
                        self.step_service.update_step(conn=conn, step=old_step)

                # Добавим новый шаг
                self.step_service.add_step(conn=conn, step=step, form_id=form_id)
                return True, "Шаг успешно добавлен"
        except Exception as e:
            return False, f"Ошибка добавления шага: {str(e)}"

    def add_form(self, form: Form) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.form_service.add_form(conn=conn, form=form)
                return True, "Форма успешно добавлена"
        except Exception as e:
            return False, f"Ошибка добавления формы: {str(e)}"

    # ================= ОБНОВЛЕНИЕ ======================
    def update_main_info(self, form: Form) -> Tuple[bool, str]:
        try:
            with self.db_manager.get_connection() as conn:
                self.form_service.update_form_main_info(conn, form=form)
                return True, "Основная информация формы успешно обновлена"
        except Exception as e:
            return False, f"Ошибка обновления основной информации формы: {str(e)}"

    def update_object(self, obj: Union[Point, Parameter, Step, BasePazzle, Track]) -> Tuple[bool, str]:
        """
        Обновление объекта в базе данных (любые подобъекты формы, но не она сама)
        """
        if obj.id is None:
            return False, "Нельзя обновить объект без id"

        try:
            with self.db_manager.get_connection() as conn:
                if isinstance(obj, Point):
                    self.point_service.update_point(conn=conn, point=obj)
                    return True, "Точка успешно обновлена"
                elif isinstance(obj, Parameter):
                    self.parameter_service.update_parameter(conn=conn, parameter=obj)
                    return True, "Параметр успешно обновлен"
                elif isinstance(obj, Step):
                    self.step_service.update_step(conn=conn, step=obj)
                    return True, "Шаг успешно обновлен"
                elif isinstance(obj, BasePazzle):
                    self.objects_service.update_object(conn=conn, base_pazzle=obj)
                    return True, "Объект HC/PC успешно обновлен"
                elif isinstance(obj, Track):
                    self.track_service.update_track(conn=conn, track=obj)
                    return True, "Трек успешно обновлен"
                else:
                    return False, f"Неизвестный тип объекта: {type(obj)}"
        except Exception as e:
            obj_type = type(obj).__name__
            return False, f"Ошибка обновления {obj_type}: {str(e)}"

    # ================= УДАЛЕНИЕ ======================
    def delete_object(self, obj: Union[Point, Parameter, Step, BasePazzle, Form, Track]) -> Tuple[bool, str]:
        """
        Удаление объекта из базы данных
        """
        if obj.id is None:
            return False, "Нельзя удалять объект без id"

        try:
            with self.db_manager.get_connection() as conn:
                if isinstance(obj, Point):
                    success = self.point_service.delete_point(conn=conn, point_id=obj.id)
                    msg = "Точка успешно удалена" if success else "Не удалось удалить точку"
                    return success, msg
                elif isinstance(obj, Parameter):
                    success = self.parameter_service.delete_parameter(conn=conn, parameter_id=obj.id)
                    msg = "Параметр успешно удален" if success else "Не удалось удалить параметр"
                    return success, msg
                elif isinstance(obj, Step):
                    success = self.step_service.delete_step(conn=conn, step_id=obj.id)
                    msg = "Шаг успешно удален" if success else "Не удалось удалить шаг"
                    return success, msg
                elif isinstance(obj, BasePazzle):
                    success = self.objects_service.delete_object(conn=conn, object_id=obj.id)
                    msg = "Объект HC/PC успешно удален" if success else "Не удалось удалить объект HC/PC"
                    return success, msg
                elif isinstance(obj, Form):
                    success = self.form_service.delete_form(conn=conn, form_id=obj.id)
                    msg = "Форма успешно удалена" if success else "Не удалось удалить форму"
                    return success, msg
                elif isinstance(obj, Track):
                    success = self.track_service.delete_track(conn=conn, track_id=obj.id)
                    msg = "Трек успешно удален" if success else "Не удалось удалить трек"
                    return success, msg
                else:
                    return False, f"Неизвестный тип объекта: {type(obj)}"
        except Exception as e:
            obj_type = type(obj).__name__
            return False, f"Ошибка удаления {obj_type}: {str(e)}"
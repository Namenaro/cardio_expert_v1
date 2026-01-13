from CORE.db.forms_services.parameter_service import ParameterService
from CORE.db.forms_services.point_service import PointService
from CORE.db.forms_services.step_service import StepService
from CORE.db.forms_services.objects_service import ObjectsService
from CORE.db.forms_services.track_service import TrackService
from CORE.db.classes_service import ClassesRepoRead
from CORE.db_dataclasses import *

import logging
from typing import List, Optional


class FormService:
    """
    Сервис для управления формами (form) и их каскадными операциями.
    Обеспечивает создание, удаление и копирование форм с сохранением
    целостности данных. Не изменяет таблицы class и *_to_class.
    """

    def __init__(self):
        """
        Инициализация сервиса форм: создает все вспомогательные сервисы для работы с шагами, точками и т.п.
        """
        classes_refs_reader = ClassesRepoRead()
        self.objects_service = ObjectsService(classes_refs_reader)
        self.track_service = TrackService(objects_service=self.objects_service)
        self.step_service = StepService(self.track_service)
        self.point_service = PointService()
        self.parameter_service = ParameterService()



    def update_form_main_info(self, conn, form: Form) -> Form:
        cursor = conn.cursor()

        cursor.execute('''
                   UPDATE form 
                   SET name = ?, comment = ?, path_to_pic = ?
                   WHERE id = ?
               ''', (form.name, form.comment, form.path_to_pic, form.id))

        logging.info(f"Осн. информация о форме {form.id} успешно обновлена")
        return form


    def add_form(self, conn, form: Form) -> Form:
        """
        Каскадно добавляет форму со всеми связанными данными.

        Args:
            conn: Соединение с базой данных
            form: Объект формы для добавления

        Returns:
            Объект Form с заполненными ID всех сущностей
        """
        cursor = conn.cursor()

        # Проверяем уникальность имени формы
        cursor.execute("SELECT id FROM form WHERE name = ?", (form.name,))
        if cursor.fetchone():
            raise ValueError(f"Form with name '{form.name}' already exists")

        # Добавляем основную форму
        cursor.execute('''
            INSERT INTO form (name, comment, path_to_pic, path_to_dataset)
            VALUES (?, ?, ?, ?)
        ''', (form.name, form.comment, form.path_to_pic, form.path_to_dataset))

        form_id = cursor.lastrowid
        form.id = form_id

        # Добавляем точки формы
        for point in form.points:
            added_point = self.point_service.add_point(conn, point, form_id)
            point.id = added_point.id

        # Добавляем параметры формы
        for parameter in form.parameters:
            added_parameter = self.parameter_service.add_parameter(conn, parameter, form_id)
            parameter.id = added_parameter.id

        # Добавляем шаги формы
        for step in form.steps:
            added_step = self.step_service.add_step(conn, step, form_id)
            step.id = added_step.id

        # Добавляем HC_PC объекты формы
        for hc_pc_object in form.HC_PC_objects:
            added_object = self.objects_service.add_object(conn, hc_pc_object, form_id=form_id)
            hc_pc_object.id = added_object.id

        # Получаем полную форму с заполненными ID
        result = self.get_form_by_id(conn, form_id)
        logging.info(f"Форма {form_id} успешно добавлена")
        return result

    def delete_form(self, conn, form_id: int) -> bool:
        """
        Каскадно удаляет форму и все связанные с ней данные.

        Args:
            conn: Соединение с базой данных
            form_id: ID формы для удаления

        Returns:
            True если удаление успешно, False если форма не найдена
        """
        cursor = conn.cursor()

        # Проверяем существование формы
        cursor.execute("SELECT id FROM form WHERE id = ?", (form_id,))
        if not cursor.fetchone():
            return False

        # Получаем все связанные сущности для каскадного удаления

        # 1. Удаляем HC_PC объекты формы
        cursor.execute("SELECT object_id FROM HC_PC_object_to_form WHERE form_id = ?", (form_id,))
        hc_pc_object_ids = [row['object_id'] for row in cursor.fetchall()]
        for object_id in hc_pc_object_ids:
            self.objects_service.delete_object(conn, object_id)

        # 2. Удаляем шаги формы (они каскадно удаляют треки и объекты)
        cursor.execute("SELECT id FROM step WHERE form_id = ?", (form_id,))
        step_ids = [row['id'] for row in cursor.fetchall()]
        for step_id in step_ids:
            self.step_service.delete_step(conn, step_id)

        # 3. Удаляем параметры формы
        cursor.execute("SELECT id FROM parameter WHERE form_id = ?", (form_id,))
        parameter_ids = [row['id'] for row in cursor.fetchall()]
        for parameter_id in parameter_ids:
            self.parameter_service.delete_parameter(conn, parameter_id)

        # 4. Удаляем точки формы
        cursor.execute("SELECT id FROM point WHERE form_id = ?", (form_id,))
        point_ids = [row['id'] for row in cursor.fetchall()]
        for point_id in point_ids:
            self.point_service.delete_point(conn, point_id)

        # 5. Удаляем саму форму
        cursor.execute("DELETE FROM form WHERE id = ?", (form_id,))

        logging.info(f"Форма {form_id} и все связанные данные успешно удалены")
        return True

    def copy_form(self, conn, form_id: int) -> Form:
        """
        Создает копию формы со всеми связанными данными.

        Args:
            conn: Соединение с базой данных
            form_id: ID формы для копирования

        Returns:
            Новая форма-копия с новыми ID
        """
        # Получаем исходную форму
        original_form = self.get_form_by_id(conn, form_id)
        if not original_form:
            raise ValueError(f"Form with ID {form_id} not found")

        # Создаем копию формы с очищенными ID
        copied_form = self._create_form_copy(original_form)

        # Добавляем новую форму в базу
        new_form = self.add_form(conn, copied_form)

        logging.info(f"Форма {form_id} успешно скопирована как форма {new_form.id}")
        return new_form

    def get_form_by_id(self, conn, form_id: int) -> Optional[Form]:
        """
        Получает форму по ID со всеми связанными данными.

        Args:
            conn: Соединение с базой данных
            form_id: ID формы

        Returns:
            Объект Form или None если не найден
        """
        cursor = conn.cursor()

        # Получаем основную информацию о форме
        cursor.execute("SELECT * FROM form WHERE id = ?", (form_id,))
        form_row = cursor.fetchone()

        if not form_row:
            return None

        # Создаем объект формы
        form = Form(
            id=form_row['id'],
            name=form_row['name'],
            comment=form_row['comment'] or "",
            path_to_pic=form_row['path_to_pic'] or "",
            path_to_dataset=form_row['path_to_dataset'] or ""
        )

        # Загружаем точки формы
        form.points = self.point_service.get_points_by_form(conn, form_id)

        # Загружаем параметры формы
        form.parameters = self.parameter_service.get_parameters_by_form(conn, form_id)

        # Загружаем шаги формы
        cursor.execute("SELECT id FROM step WHERE form_id = ? ORDER BY num_in_form", (form_id,))
        step_ids = [row['id'] for row in cursor.fetchall()]
        for step_id in step_ids:
            step = self.step_service.get_step_by_id(conn, step_id)
            if step:
                form.steps.append(step)

        # Загружаем HC_PC объекты формы
        form.HC_PC_objects = self.objects_service.get_objects_by_form(conn, form_id)

        return form

    def get_all_forms(self, conn) -> List[Form]:
        """
        Получает список всех форм базы данных.

        Args:
            conn: Соединение с базой данных

        Returns:
            Список форм с заполненными только id, name, comment
        """
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, comment FROM form")
        rows = cursor.fetchall()

        forms = []
        for row in rows:
            forms.append(Form(
                id=row['id'],
                name=row['name'],
                comment=row['comment'] or ""
            ))

        return forms

    def _create_form_copy(self, original_form: Form) -> Form:
        """Создает копию формы с очищенными ID и уникальным именем"""
        import uuid

        # Генерируем уникальный суффикс для имени
        unique_suffix = str(uuid.uuid4())[:8]
        new_name = f"{original_form.name}_copy_{unique_suffix}"

        # Создаем копию с очищенными ID
        copied_form = Form(
            name=new_name,
            comment=original_form.comment,
            path_to_pic=original_form.path_to_pic,
            path_to_dataset=original_form.path_to_dataset
        )

        # Копируем точки (очищаем ID)
        for point in original_form.points:
            copied_form.points.append(Point(
                name=point.name,
                comment=point.comment
            ))

        # Копируем параметры (очищаем ID)
        for parameter in original_form.parameters:
            copied_form.parameters.append(Parameter(
                name=parameter.name,
                comment=parameter.comment,
                data_type=parameter.data_type
            ))

        # Копируем шаги (очищаем ID, но сохраняем структуру)
        for step in original_form.steps:
            copied_step = Step(
                num_in_form=step.num_in_form,
                target_point=Point(name=step.target_point.name,
                                   comment=step.target_point.comment) if step.target_point else None,
                left_point=Point(name=step.left_point.name,
                                 comment=step.left_point.comment) if step.left_point else None,
                right_point=Point(name=step.right_point.name,
                                  comment=step.right_point.comment) if step.right_point else None,
                left_padding_t=step.left_padding_t,
                right_padding_t=step.right_padding_t,
                comment=step.comment
            )

            # Копируем треки шага
            for track in step.tracks:
                copied_track = Track()

                # Копируем SMs (очищаем ID)
                for sm in track.SMs:
                    copied_sm = BasePazzle(
                        name=sm.name,
                        comment=sm.comment,
                        class_ref=sm.class_ref  # class_ref не очищаем - ссылается на существующий класс
                    )
                    # Копируем связанные данные объектов...
                    copied_track.SMs.append(copied_sm)

                # Копируем PSs (очищаем ID)
                for ps in track.PSs:
                    copied_ps = BasePazzle(
                        name=ps.name,
                        comment=ps.comment,
                        class_ref=ps.class_ref  # class_ref не очищаем
                    )
                    # Копируем связанные данные объектов...
                    copied_track.PSs.append(copied_ps)

                copied_step.tracks.append(copied_track)

            copied_form.steps.append(copied_step)

        # Копируем HC_PC объекты (очищаем ID)
        for hc_pc_object in original_form.HC_PC_objects:
            copied_object = BasePazzle(
                name=hc_pc_object.name,
                comment=hc_pc_object.comment,
                class_ref=hc_pc_object.class_ref  # class_ref не очищаем
            )
            # Копируем связанные данные объектов...
            copied_form.HC_PC_objects.append(copied_object)

        return copied_form
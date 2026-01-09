from CORE.db_dataclasses import *
from CORE.db.forms_services.object_relation_service import ObjectRelationService
from CORE.db.forms_services.object_data_service import ObjectDataService

import logging
from typing import List, Optional, Tuple

from CORE.db.classes_service import ClassesRepoRead

class ObjectsService:
    """
    Главный фасад-сервис для комплексного управления объектами BasePazzle.
    Объединяет функциональность ObjectDataService и ObjectRelationService,
    предоставляя высокоуровневые операции CRUD с каскадным обновлением данных.
    Обрабатывает бизнес-логику при изменении класса объекта и управляет транзакционной целостностью.
    """

    def __init__(self, classes_refs_reader:ClassesRepoRead):
        self.data_service = ObjectDataService()
        self.relation_service = ObjectRelationService(classes_refs_reader)


    def delete_object(self, conn, object_id: int) -> bool:
        """
        Удаляет объект и все связанные с ним данные каскадно
        """
        cursor = conn.cursor()

        # Проверяем существование объекта
        cursor.execute("SELECT id FROM object WHERE id = ?", (object_id,))
        if not cursor.fetchone():
            return False

        # Удаляем в правильном порядке (от дочерних к родительским)
        tables_to_delete = [
            'value_to_argument',
            'value_to_input_param',
            'value_to_input_point',
            'value_to_output_param',
            'object_to_track',
            'HC_PC_object_to_form',
            'object'
        ]

        for table in tables_to_delete:
            if table == 'object':
                cursor.execute(f"DELETE FROM {table} WHERE id = ?", (object_id,))
            else:
                cursor.execute(f"DELETE FROM {table} WHERE object_id = ?", (object_id,))

        logging.info(f"Объект {object_id} успешно удален")
        return True

    def add_object(self, conn, base_pazzle: BasePazzle,
                   form_id: Optional[int] = None,
                   track_id: Optional[int] = None,
                   num_in_track: Optional[int] = -1) -> BasePazzle:
        """
        Добавляет новый объект в базу данных каскадно.
        Если пазл типа PC/HC, то указать form_id
        Если пазл типа PS SM, указать привязку к треку "
        num_in_track = -1 в случае, если добавляется объект PS
        """
        cursor = conn.cursor()

        # Валидация class_ref
        if not base_pazzle.class_ref or not base_pazzle.class_ref.id:
            raise ValueError("Class reference must have ID")

        # Добавляем основной объект
        cursor.execute('''
            INSERT INTO object (class_id, name, comment)
            VALUES (?, ?, ?)
        ''', (base_pazzle.class_ref.id, base_pazzle.name, base_pazzle.comment))

        object_id = cursor.lastrowid
        base_pazzle.id = object_id

        # Добавляем связанные данные
        self.data_service._add_related_data(cursor, object_id, base_pazzle)

        # Добавляем связи
        if form_id is not None: # напрямую к форме привязываем HC|PC
            self.relation_service.add_object_to_form(cursor, object_id, form_id)
        elif track_id is not None: # Это SM или PS
            self.relation_service.add_object_to_track(cursor, object_id, track_id, num_in_track)
        else:
            raise ValueError("Нарушено соглашение: Если пазл типа PC/HC, то указать form_id, иначе указать привязку к треку")

        # Получаем полный объект с заполненными ID
        result = self.relation_service._get_full_object(conn, object_id)
        logging.info(f"Объект {object_id} успешно добавлен")
        return result

    def update_object(self, conn, base_pazzle: BasePazzle, num_in_track: int = -1) -> BasePazzle:
        """
        Обновляет объект в базе данных каскадно
        """
        if not base_pazzle.id:
            raise ValueError("Object ID is required for update")

        cursor = conn.cursor()

        # Получаем текущую версию объекта
        current_object = self.relation_service._get_full_object(conn, base_pazzle.id)
        if not current_object:
            raise ValueError(f"Object with ID {base_pazzle.id} not found")

        # Проверяем, изменился ли class_id
        class_changed = (current_object.class_ref.id != base_pazzle.class_ref.id)

        # Обновляем основной объект
        cursor.execute('''
            UPDATE object 
            SET class_id = ?, name = ?, comment = ?
            WHERE id = ?
        ''', (base_pazzle.class_ref.id, base_pazzle.name, base_pazzle.comment, base_pazzle.id))

        if class_changed:
            # Если класс изменился - полностью удаляем и пересоздаем связанные данные
            self.data_service._delete_related_data(cursor, base_pazzle.id)
            self.data_service._add_related_data(cursor, base_pazzle.id, base_pazzle)
        else:
            # Если класс не изменился - точечно обновляем связанные данные
            self.data_service._update_related_data(cursor, base_pazzle.id, base_pazzle, current_object)

        if current_object.is_SM():
            self.relation_service.change_num_in_track(cursor, current_object.id, num_in_track)

        # Получаем обновленный объект
        result = self.relation_service._get_full_object(conn, base_pazzle.id)
        logging.info(f"Объект {base_pazzle.id} успешно обновлен")
        return result

    def get_object_by_id(self, conn, object_id: int) -> Optional[BasePazzle]:
        """Получает объект по ID"""
        return self.relation_service._get_full_object(conn, object_id)

    def get_objects_by_class(self, conn, class_id: int) -> List[BasePazzle]:
        """Получает все объекты определенного класса"""
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM object WHERE class_id = ?', (class_id,))
        object_ids = [row['id'] for row in cursor.fetchall()]

        objects = []
        for obj_id in object_ids:
            obj = self.relation_service._get_full_object(conn, obj_id)
            if obj:
                objects.append(obj)

        return objects

    # Делегируем методы сервису связей
    def get_objects_by_form(self, conn, form_id: int) -> List[BasePazzle]:
        return self.relation_service.get_objects_by_form(conn, form_id)

    def get_objects_by_track(self, conn, track_id: int) -> List[Tuple[BasePazzle, int]]:
        return self.relation_service.get_objects_by_track(conn, track_id)
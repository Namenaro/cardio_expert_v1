import sqlite3
from typing import Optional, List
from CORE.database.repositories.objects_helpers_repos import *
from CORE.db_dataclasses import BasePazzle


class ObjectsService:
    """Фасадный сервис для работы со всеми репозиториями объектов"""

    def __init__(self):
        self.objects_repo = ObjectsRepo()
        self.argument_values_repo = ArgumentValuesRepo()
        self.input_param_values_repo = InputParamValuesRepo()
        self.input_point_values_repo = InputPointValuesRepo()
        self.output_param_values_repo = OutputParamValuesRepo()

    def get_full_object(self, conn: sqlite3.Connection, object_id: int) -> Optional[BasePazzle]:
        """Получает полную информацию об объекте со всеми связанными значениями"""
        obj = self.objects_repo.get_object_by_id(conn, object_id)
        if not obj:
            return None

        # Загружаем все связанные значения
        obj.argument_values = self.argument_values_repo.get_argument_values_by_object(conn, object_id)
        obj.input_param_values = self.input_param_values_repo.get_input_param_values_by_object(conn, object_id)
        obj.input_point_values = self.input_point_values_repo.get_input_point_values_by_object(conn, object_id)
        obj.output_param_values = self.output_param_values_repo.get_output_param_values_by_object(conn, object_id)

        return obj

    def delete_object_completely(self, conn: sqlite3.Connection, object_id: int) -> bool:
        """Полностью удаляет объект со всеми связанными значениями"""
        try:
            # Удаляем все связанные значения
            self.argument_values_repo._execute_commit(conn,
                                                      'DELETE FROM value_to_argument WHERE object_id = ?', (object_id,))
            self.input_param_values_repo._execute_commit(conn,
                                                         'DELETE FROM value_to_input_param WHERE object_id = ?',
                                                         (object_id,))
            self.input_point_values_repo._execute_commit(conn,
                                                         'DELETE FROM value_to_input_point WHERE object_id = ?',
                                                         (object_id,))
            self.output_param_values_repo._execute_commit(conn,
                                                          'DELETE FROM value_to_output_param WHERE object_id = ?',
                                                          (object_id,))

            # Удаляем сам объект
            return self.objects_repo.delete_object(conn, object_id)
        except sqlite3.Error as e:
            print(f"Ошибка при полном удалении объекта: {e}")
            conn.rollback()
            return False
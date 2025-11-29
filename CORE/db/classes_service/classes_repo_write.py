from CORE.pazzles_lib import FoldersParser
from CORE.db.db_manager import DBManager
from CORE.db_dataclasses import BaseClass

import sqlite3
from typing import List

class ClassesRepoWrite:
    """Репозиторий для работы с классами в базе данных"""

    def __init__(self, db: DBManager):
        self.db = db

    def save_all_classes(self,
                 pc_list: List[BaseClass],
                 hc_list: List[BaseClass],
                 ps_list: List[BaseClass],
                 sm_list: List[BaseClass]) -> None:
        """Сохраняет все классы и их связанные данные в базу"""
        self.all_classes = pc_list + hc_list + ps_list + sm_list

        with self.db.get_connection() as conn:
            # Сохраняем/обновляем классы и получаем их ID
            class_ids = self._save_or_update_classes(conn)

            # ОБНОВЛЯЕМ связанные данные (удаляем старые, добавляем новые)
            self._update_constructor_arguments(conn, class_ids)
            self._update_input_points(conn, class_ids)
            self._update_input_params(conn, class_ids)
            self._update_output_params(conn, class_ids)

            conn.commit()

    def _save_or_update_classes(self, conn: sqlite3.Connection) -> dict:
        """Сохраняет или обновляет классы и возвращает словарь {имя_класса: id}"""
        class_ids = {}

        # Пробуем обновить, если не получилось - вставляем новый
        update_sql = """
            UPDATE class 
            SET comment = ?, TYPE = ?
            WHERE name = ?
        """

        insert_sql = """
            INSERT INTO class (name, comment, TYPE)
            VALUES (?, ?, ?)
        """

        for class_info in self.all_classes:
            try:
                # Пробуем обновить существующий класс
                cursor = conn.execute(update_sql, (
                    class_info.comment,
                    class_info.type,
                    class_info.name
                ))

                if cursor.rowcount > 0:
                    # Класс был обновлен - получаем его ID
                    cursor = conn.execute("SELECT id FROM class WHERE name = ?", (class_info.name,))
                    result = cursor.fetchone()
                    class_ids[class_info.name] = result['id']
                    print(f"↻ Обновлен класс: {class_info.name} (ID: {result['id']})")
                else:
                    # Класс не существует - вставляем новый
                    cursor = conn.execute(insert_sql, (
                        class_info.name,
                        class_info.comment,
                        class_info.type
                    ))
                    class_ids[class_info.name] = cursor.lastrowid
                    print(f"✓ Добавлен класс: {class_info.name} (ID: {cursor.lastrowid})")

            except sqlite3.Error as e:
                print(f"✗ Ошибка при сохранении класса {class_info.name}: {e}")

        return class_ids

    def _update_constructor_arguments(self, conn: sqlite3.Connection, class_ids: dict) -> None:
        """Полностью обновляет аргументы конструкторов для классов"""
        delete_sql = "DELETE FROM argument_to_class WHERE class_id = ?"
        insert_sql = """
            INSERT INTO argument_to_class (class_id, name, comment, data_type, default_value)
            VALUES (?, ?, ?, ?, ?)
        """

        for class_info in self.all_classes:
            class_id = class_ids.get(class_info.name)
            if not class_id:
                continue

            # Удаляем старые аргументы
            conn.execute(delete_sql, (class_id,))

            # Добавляем новые аргументы
            for arg in class_info.constructor_arguments:
                try:
                    conn.execute(insert_sql, (
                        class_id,
                        arg.name,
                        arg.comment,
                        arg.data_type,
                        arg.default_value
                    ))
                    print(f"  ✓ Аргумент конструктора: {arg.name}")
                except sqlite3.Error as e:
                    print(f"  ✗ Ошибка при сохранении аргумента {arg.name}: {e}")

    def _update_input_points(self, conn: sqlite3.Connection, class_ids: dict) -> None:
        """Полностью обновляет входные точки для классов"""
        delete_sql = "DELETE FROM input_point_to_class WHERE class_id = ?"
        insert_sql = """
            INSERT INTO input_point_to_class (class_id, name, comment)
            VALUES (?, ?, ?)
        """

        for class_info in self.all_classes:
            class_id = class_ids.get(class_info.name)
            if not class_id:
                continue

            # Удаляем старые точки
            conn.execute(delete_sql, (class_id,))

            # Добавляем новые точки
            for point in class_info.input_points:
                try:
                    conn.execute(insert_sql, (
                        class_id,
                        point.name,
                        point.comment
                    ))
                    print(f"  ✓ Входная точка: {point.name}")
                except sqlite3.Error as e:
                    print(f"  ✗ Ошибка при сохранении точки {point.name}: {e}")

    def _update_input_params(self, conn: sqlite3.Connection, class_ids: dict) -> None:
        """Полностью обновляет входные параметры для классов"""
        delete_sql = "DELETE FROM input_param_to_class WHERE class_id = ?"
        insert_sql = """
            INSERT INTO input_param_to_class (class_id, name, comment, data_type)
            VALUES (?, ?, ?, ?)
        """

        for class_info in self.all_classes:
            class_id = class_ids.get(class_info.name)
            if not class_id:
                continue

            # Удаляем старые параметры
            conn.execute(delete_sql, (class_id,))

            # Добавляем новые параметры
            for param in class_info.input_params:
                try:
                    conn.execute(insert_sql, (
                        class_id,
                        param.name,
                        param.comment,
                        param.data_type
                    ))
                    print(f"  ✓ Входной параметр: {param.name}")
                except sqlite3.Error as e:
                    print(f"  ✗ Ошибка при сохранении параметра {param.name}: {e}")

    def _update_output_params(self, conn: sqlite3.Connection, class_ids: dict) -> None:
        """Полностью обновляет выходные параметры для классов"""
        delete_sql = "DELETE FROM output_param_to_class WHERE class_id = ?"
        insert_sql = """
            INSERT INTO output_param_to_class (class_id, name, comment, data_type)
            VALUES (?, ?, ?, ?)
        """

        for class_info in self.all_classes:
            class_id = class_ids.get(class_info.name)
            if not class_id:
                continue

            # Удаляем старые параметры
            conn.execute(delete_sql, (class_id,))

            # Добавляем новые параметры
            for param in class_info.output_params:
                try:
                    conn.execute(insert_sql, (
                        class_id,
                        param.name,
                        param.comment,
                        param.data_type
                    ))
                    print(f"  ✓ Выходной параметр: {param.name}")
                except sqlite3.Error as e:
                    print(f"  ✗ Ошибка при сохранении параметра {param.name}: {e}")


def add_all_classes_to_db(db_manager):
    # Парсим классы из папок
    folders_parser = FoldersParser()
    pc_list, hc_list, ps_list, sm_list = folders_parser.parse_all_folders()

    # Создаем репозиторий и сохраняем данные
    repo = ClassesRepoWrite(db_manager)
    repo.save_all_classes(pc_list, hc_list, ps_list, sm_list)


# Пример применения
if __name__ == "__main__":
    db_manager = DBManager()
    db_manager.delete_database()
    db_manager.create_tables()
    add_all_classes_to_db(db_manager)
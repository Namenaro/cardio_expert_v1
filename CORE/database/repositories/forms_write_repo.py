from CORE.db_dataclasses import Form, Track, Point,  Parameter, BaseClass, BasePazzle
from CORE.database.db_manager import DBManager

from CORE.database.repositories.points_repo import PointsRepo


import sqlite3
from sqlite3 import Cursor


from typing import List, Optional, Dict
import logging

class FormsWriteRepo:
    def __init__(self, db: DBManager) -> None:
        """Инициализация репозитория"""
        self.db = db
        self._points_repo = PointsRepo()


    def add_new_form(self, form: Form) -> Optional[int]:
        """Сохранение формы в базу данных в одной транзакции"""
        conn = self.db.get_connection()

        try:
            conn.execute("BEGIN")

            # 1. Создаем основную запись формы
            form_id = self._insert_form(conn, form)
            if not form_id:
                conn.rollback()
                return None


            conn.commit()
            return form_id


        except Exception as e:
            conn.rollback()
            logging.error(f"Ошибка создания формы '{form.name}': {e}")
            return None

        finally:
            self.db.close_connection(conn)

    def _insert_form(self, conn: sqlite3.Connection, form: Form) -> Optional[int]:
        """Добавляет основную запись формы"""
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO form (name, comment, path_to_pic, path_to_dataset)
                VALUES (?, ?, ?, ?)
            """, (form.name, form.comment, form.path_to_pic, form.path_to_dataset))
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logging.error(f"Форма с именем '{form.name}' уже существует: {e}")
            return None
        except Exception as e:
            logging.error(f"Ошибка вставки формы: {e}")
            return None






if __name__ == "__main__":
    db_manager = DBManager()

    if db_manager.db_exists():
        db_manager.delete_database()
    db_manager.create_tables()


    repo = FormsWriteRepo(db_manager)

    test_form = Form(name="test_form",
                     comment="комментарий",
                     path_to_pic="\путь к картике",
                     path_to_dataset="\путь к датасету")

    test_form.points.append(Point(name="point1", comment="коммент"))
    test_form.points.append(Point(name="point2", comment="коммент"))

    test_form.parameters.append(Parameter(name="param1", comment="коммент"))
    test_form.parameters.append(Parameter(name="param2", comment="коммент"))

    track = Track()

    id = repo.add_new_form(test_form)
    print(id)





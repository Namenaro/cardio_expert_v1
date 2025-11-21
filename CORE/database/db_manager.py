from CORE.settings import DB_PATH
from CORE.database.schema import create_tables

import sqlite3
import os
import logging
from contextlib import contextmanager


class DBManager:
    """
    Управляет созданием/удалением базы и получением соединения с ней
    """
    def __init__(self, db_path:str = DB_PATH):
        self.db_path = db_path

    def db_exists(self) -> bool:
        """Проверяет существование базы данных"""
        return os.path.exists(self.db_path)

    def create_tables(self):
        """Создает все таблицы в базе данных"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            create_tables(cursor)
            logging.info("Таблицы успешно созданы")

    def delete_database(self) -> bool:
        """Удаляет базу данных"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            return True
        return False


    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()





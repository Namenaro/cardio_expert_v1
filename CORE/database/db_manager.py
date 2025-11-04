from CORE.settings import DB_PATH
from CORE.database.schema import create_tables

import sqlite3
import os
from typing import Optional
import logging

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
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            create_tables(cursor)

            conn.commit()
            logging.info("Таблицы успешно созданы")

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_database(self) -> bool:
        """Удаляет базу данных"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            return True
        return False

    def get_connection(self) -> sqlite3.Connection:
        """
        Возвращает новое подключение к БД.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        return conn





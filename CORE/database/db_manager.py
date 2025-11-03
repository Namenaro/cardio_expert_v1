from CORE.settings import DB_PATH
from CORE.database.schema import create_tables

import sqlite3
import os
from typing import Optional

class DBManager:
    def __init__(self, db_path = DB_PATH):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def db_exists(self) -> bool:
        """
        Проверяет существование базы данных

        Returns:
            True если база существует, False если нет
        """
        return os.path.exists(self.db_path)


    def create_tables(self):
        """Создает все таблицы в базе данных"""
        connection = self.get_connection()
        cursor = connection.cursor()
        create_tables(cursor)

        connection.commit()
        self.close()
        print(print("Таблицы успешно созданы"))


    def delete_database(self) -> bool:
        """
        Удаляет базу данных

        Returns:
            True если база удалена, False если не существовала
        """
        self.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            return True
        return False

    def get_connection(self) -> sqlite3.Connection:
        """
        Возвращает подключение к БД.
        Создает новое при первом вызове, затем возвращает существующее.

        Returns:
            Активное подключение к базе данных
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection


    def close(self)-> None:
        """Закрывает подключение"""
        if self._connection:
            self._connection.close()
            self._connection = None




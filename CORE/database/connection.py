import sqlite3
import os
from typing import Optional
from CORE.settings import DB_PATH


class DatabaseConnection:
    """Класс для управления подключением к SQLite базе данных"""

    def __init__(self, db_path: str = DB_PATH) -> None:
        """
        Инициализация подключения к базе данных

        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

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

    def close(self) -> None:
        """Закрывает подключение"""
        if self._connection:
            self._connection.close()
            self._connection = None
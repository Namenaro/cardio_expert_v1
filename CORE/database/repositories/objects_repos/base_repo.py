# base_repo.py
import sqlite3
from typing import Optional, List


class BaseRepo:
    """Базовый репозиторий с общими методами"""

    @staticmethod
    def _execute_commit(conn: sqlite3.Connection, query: str, params: tuple) -> bool:
        """Выполняет запрос с коммитом"""
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            conn.rollback()
            return False

    @staticmethod
    def _execute_fetchall(conn: sqlite3.Connection, query: str, params: tuple) -> List[sqlite3.Row]:
        """Выполняет запрос на чтение"""
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return []

    @staticmethod
    def _execute_fetchone(conn: sqlite3.Connection, query: str, params: tuple) -> Optional[sqlite3.Row]:
        """Выполняет запрос на чтение одной строки"""
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None
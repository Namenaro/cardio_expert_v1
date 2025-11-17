# base_repo.py
import logging
import sqlite3
from typing import Optional, List

logger = logging.getLogger(__name__)

class BaseRepo:
    """Базовый репозиторий с общими методами"""

    @staticmethod
    def _execute_commit(conn: sqlite3.Connection, query: str, params: tuple) -> bool:
        """Выполняет запрос на изменение данных с подтверждением транзакции

        Используется для INSERT, UPDATE, DELETE операций, которые требуют
        подтверждения изменений в базе данных.

        Args:
            conn: SQLite соединение для выполнения запроса
            query: SQL запрос на изменение данных (INSERT/UPDATE/DELETE)
            params: параметры для подстановки в запрос

        Returns:
            bool:
                - True, если запрос затронул одну или более строк
                - False, если ни одна строка не была изменена

        Raises:
            sqlite3.Error: при ошибках выполнения запроса или конфликтах ограничений

        Note:
            Метод выполняет conn.commit() только при успешном выполнении запроса.
            При возникновении исключения транзакция должна быть откатана вызывающим кодом.

        Example:
            >>> success = _execute_commit(conn, "UPDATE users SET active = ? WHERE id = ?", (True, 1))
            >>> if success:
            ...     print("Пользователь обновлен")
            ... else:
            ...     print("Пользователь не найден")
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения запроса: {e}")
            raise

    @staticmethod
    def _execute_fetchall(conn: sqlite3.Connection, query: str, params: tuple) -> List[sqlite3.Row]:
        """Выполняет запрос на чтение

        Args:
            conn: SQLite соединение
            query: SQL запрос
            params: параметры запроса

        Returns:
            List[sqlite3.Row]: список строк результата

        Raises:
            sqlite3.Error: при ошибках выполнения запроса
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения запроса: {e}\nЗапрос: {query}\nПараметры: {params}")
            raise

    @staticmethod
    def _execute_fetchone(conn: sqlite3.Connection, query: str, params: tuple) -> Optional[sqlite3.Row]:
        """Выполняет запрос на чтение одной строки

        Args:
            conn: SQLite соединение для выполнения запроса
            query: SQL запрос с плейсхолдерами
            params: параметры для подстановки в запрос

        Returns:
            Optional[sqlite3.Row]: одна строка результата или None, если строк нет

        Raises:
            sqlite3.Error: при ошибках выполнения запроса (ошибки синтаксиса,
                          нарушения ограничений, проблемы с соединением и т.д.)


        """
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Ошибка выполнения запроса: {e}\nЗапрос: {query}\nПараметры: {params}")
            raise
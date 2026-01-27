"""
Простая конфигурация логирования для приложения
"""
import logging
import sys
import os
from typing import Optional


class AppLogger:
    """Класс для управления глобальным логированием приложения"""

    ROOT_LOGGER = logging.getLogger('')  # Корневой логгер Python
    _default_level = logging.WARNING
    _default_format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    _default_handler = None

    @classmethod
    def setup(
            cls,
            level: int = logging.WARNING,
            format_str: Optional[str] = None,
            handler: Optional[logging.Handler] = None,
            log_file: Optional[str] = None,
            clear_log_on_start: bool = True  # Флаг очистки файла
    ) -> None:
        """
        Настройка глобального логирования.

        Args:
            level: Уровень логирования.
            format_str: Формат логов.
            handler: Обработчик (если None, используется StreamHandler).
            log_file: Путь к файлу лога (если указан, добавляется файловый обработчик).
            clear_log_on_start: Если True, файл лога очищается при старте.
        """
        cls._default_level = level
        if format_str:
            cls._default_format = format_str

        # Создаём обработчики
        handlers = []

        # Консольный обработчик
        if handler is None:
            handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(cls._default_format)
        handler.setFormatter(formatter)
        handlers.append(handler)

        # Файловый обработчик (если указан файл)
        if log_file:
            # Очищаем файл, если нужно
            if clear_log_on_start and os.path.exists(log_file):
                open(log_file, 'w').close()  # Полное очищение

            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)

        # Настраиваем корневой логгер
        cls.ROOT_LOGGER.setLevel(level)
        cls.ROOT_LOGGER.handlers = []  # Очищаем старые обработчики
        for h in handlers:
            cls.ROOT_LOGGER.addHandler(h)

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Получение логгера с именем."""
        logger = logging.getLogger(name)
        logger.setLevel(cls._default_level)
        return logger


# Глобальный экземпляр
logger = AppLogger()


def setup_logging(
        level: int = logging.INFO,
        log_file: Optional[str] = None,
        clear_log_on_start: bool = True
):
    """Простая настройка логирования."""
    AppLogger.setup(level=level, log_file=log_file, clear_log_on_start=clear_log_on_start)

def get_logger(name: str) -> logging.Logger:
    """Получение логгера."""
    return AppLogger.get_logger(name)

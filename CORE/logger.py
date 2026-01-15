"""
Простая конфигурация логирования для библиотеки CORE
"""
import logging
import sys
from typing import Optional


class CoreLogger:
    """Простой класс для управления логированием CORE"""

    ROOT_NAME = "core"

    # Глобальные настройки по умолчанию
    _default_level = logging.WARNING
    _default_format = "%(name)s - %(levelname)s - %(message)s"
    _default_handler = None

    @classmethod
    def setup(cls,
              level: int = logging.WARNING,
              format_str: Optional[str] = None,
              handler: Optional[logging.Handler] = None) -> None:
        """
        Настройка логирования для всей библиотеки CORE

        Args:
            level: Уровень логирования
            format_str: Формат логов (если None, используется формат по умолчанию)
            handler: Обработчик (если None, используется StreamHandler)
        """
        # Сохраняем настройки
        cls._default_level = level
        if format_str:
            cls._default_format = format_str

        # Создаем обработчик по умолчанию если не передан
        if handler is None:
            handler = logging.StreamHandler(sys.stdout)

        # Настраиваем форматтер
        formatter = logging.Formatter(cls._default_format)
        handler.setFormatter(formatter)
        cls._default_handler = handler

        # Настраиваем корневой логгер CORE
        root_logger = logging.getLogger(cls.ROOT_NAME)
        root_logger.setLevel(level)
        root_logger.handlers = []  # Очищаем старые обработчики
        root_logger.addHandler(handler)
        root_logger.propagate = False

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Получение логгера с именем

        Args:
            name: Имя логгера (например 'core.form_dataset')

        Returns:
            Настроенный логгер
        """
        # Добавляем префикс 'core.' если не указан
        if not name.startswith(cls.ROOT_NAME):
            name = f"{cls.ROOT_NAME}.{name}"

        # Получаем логгер
        logger = logging.getLogger(name)

        # Если у логгера нет обработчиков, наследуем от корневого
        if not logger.handlers and logger.parent:
            logger.setLevel(cls._default_level)
            if cls._default_handler:
                logger.addHandler(cls._default_handler)

        return logger


# Создаем глобальный экземпляр
logger = CoreLogger()


def setup_logging(level: int = logging.WARNING):
    """Простая настройка логирования"""
    CoreLogger.setup(level=level)


def get_logger(name: str) -> logging.Logger:
    """Получение логгера"""
    return CoreLogger.get_logger(name)

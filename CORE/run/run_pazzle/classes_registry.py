import sys
from typing import Dict, Type, get_type_hints, get_args, get_origin
import importlib
import inspect
import os
import pkgutil

from CORE.logger import get_logger

logger = get_logger(__name__)


class ClassesRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Проверяем, чтобы инициализация была только один раз
        if not hasattr(self, '_initialized'):
            self._registry = {}
            self._initialized = True
            self.auto_discover()


    def register(self, name: str, cls: Type):
        self._registry[name] = cls

    def auto_discover(self):
        """Автоматически находит все классы во всех подпапках пакета"""
        import CORE.pazzles_lib

        # Сохраняем базовый пакет
        base_package = CORE.pazzles_lib.__name__  # "CORE.pazzles_lib"

        # Список папок для поиска
        subfolders = ['HC', 'PC', 'PS', 'SM']

        for subfolder in subfolders:
            # Полный путь к подпапке
            subfolder_path = os.path.join(CORE.pazzles_lib.__path__[0], subfolder)

            # Проверяем, существует ли папка
            if not os.path.isdir(subfolder_path):
                continue

            # Ищем модули в этой папке
            for _, module_name, _ in pkgutil.iter_modules([subfolder_path]):
                try:
                    # Импортируем модуль с полным путем
                    module = importlib.import_module(f"{base_package}.{subfolder}.{module_name}")

                    # Регистрируем все подходящие классы
                    for name, obj in inspect.getmembers(module):
                        if self._is_valid_class(obj, module):
                            self.register(name, obj)

                except Exception as e:
                    logger.error(f"Warning: Не смогли загрузить модуль {subfolder}.{module_name}: {e}")
                    continue

    def _is_valid_class(self, obj, module):
        """Проверяет, подходит ли класс для регистрации"""
        return (
                inspect.isclass(obj) and
                obj.__module__ == module.__name__ and
                hasattr(obj, 'run')
        )

    def __getitem__(self, key: str) -> Type:
        """
        Позволяет обращаться к зарегистрированным классам через квадратные скобки.

        Args:
            key: Имя класса (ключ в реестре)

        Returns:
            Класс, зарегистрированный под данным именем

        Raises:
            KeyError: Если класс с таким именем не найден в реестре
        """
        if key not in self._registry:
            raise KeyError(
                f"Класс '{key}' не найден в реестре. Доступные классы: {'\\n'.join(list(self._registry.keys()))}")
        return self._registry[key]

    def get_available_classes(self):
        """Возвращает список доступных классов"""
        return list(self._registry.keys())


# Экспортируем синглтон
classes_registry = ClassesRegistry()

from typing import Dict, Type, get_type_hints, get_args, get_origin
import importlib
import inspect
import os
import pkgutil


class PuzzleFactory:
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

        # Список папок для поиска
        subfolders = ['НС', 'PC', 'PS', 'SM']

        for subfolder in subfolders:
            # Полный путь к подпапке
            subfolder_path = os.path.join(CORE.pazzles_lib.__path__[0], subfolder)

            # Проверяем, существует ли папка
            if not os.path.isdir(subfolder_path):
                continue

            # Ищем модули в этой папке
            for _, module_name, _ in pkgutil.iter_modules([subfolder_path]):
                try:
                    # Импортируем модуль из подпапки
                    module = importlib.import_module(f"pazzles_lib.{subfolder}.{module_name}")

                    # Регистрируем все подходящие классы
                    for name, obj in inspect.getmembers(module):
                        if self._is_valid_class(obj, module):
                            self.register(name, obj)
                except Exception as e:
                    print(f"Warning: Failed to load module {subfolder}.{module_name}: {e}")
                    continue

    def _is_valid_class(self, obj, module):
        """Проверяет, подходит ли класс для регистрации"""
        return (
                inspect.isclass(obj) and
                obj.__module__ == module.__name__ and
                hasattr(obj, 'run')
        )

    def _convert_value(self, value: str, target_type):
        """Преобразует строку в указанный тип"""
        if value is None:
            raise ValueError("Value cannot be None")
        if value == "":
            raise ValueError("Value cannot be empty string")

        # Обработка list[int] и list[float]
        origin = get_origin(target_type)
        if origin is list:
            args = get_args(target_type)
            if len(args) == 1:
                elem_type = args[0]
                # Удаляем скобки и разбиваем по запятым
                value = value.strip('[] ')
                if not value:
                    raise ValueError("List cannot be empty")
                elements = [elem.strip() for elem in value.split(',') if elem.strip()]

                if elem_type == int:
                    return [int(elem) for elem in elements]
                elif elem_type == float:
                    return [float(elem) for elem in elements]

        # Базовые типы
        if target_type == bool:
            val_lower = value.lower()
            if val_lower == 'true':
                return True
            elif val_lower == 'false':
                return False
            else:
                raise ValueError(f"Bool must be 'true' or 'false', got: {value}")
        elif target_type == int:
            return int(value)
        elif target_type == float:
            return float(value)
        elif target_type == str:
            return str(value)

        raise ValueError(f"Unsupported type: {target_type}")

    def create(self, classname: str, args: Dict[str, str]):
        """Создает объект класса с преобразованием типов"""
        if classname not in self._registry:
            raise ValueError(f"Class {classname} not found")

        cls = self._registry[classname]
        signature = inspect.signature(cls.__init__)
        type_hints = get_type_hints(cls.__init__)

        prepared_args = {}

        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue

            if param_name in args:
                value = args[param_name]
                expected_type = type_hints.get(param_name, str)

                try:
                    prepared_args[param_name] = self._convert_value(value, expected_type)
                except Exception as e:
                    raise ValueError(
                        f"Failed to convert '{param_name}'='{value}' to {expected_type}: {e}"
                    )
            elif param.default != inspect.Parameter.empty:
                prepared_args[param_name] = param.default
            else:
                raise ValueError(f"Missing required argument: {param_name}")

        return cls(**prepared_args)

    def get_available_classes(self):
        """Возвращает список доступных классов"""
        return list(self._registry.keys())


# Экспортируем синглтон
factory = PuzzleFactory()

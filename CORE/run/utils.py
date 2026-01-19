import os
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Type


def discover_puzzle_classes(package_path: str) -> Dict[str, Type]:
    """
    Автоматически находит все классы в .py-файлах указанного пакета.

    Args:
        package_path: путь к пакету (например, "CORE/puzzles_lib")

    Returns:
        Словарь: {имя_класса: класс}
    """
    classes = {}
    package_dir = Path(package_path)

    # Проходим по всем .py файлам в директории
    for py_file in package_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue  # пропускаем __init__.py

        # Имя модуля (без .py)
        module_name = py_file.stem

        # Полный путь к файлу
        file_path = str(py_file)

        # Загружаем модуль
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Ищем классы в модуле
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # Проверяем, что это класс, определён в этом модуле и не является встроенным
            if (
                    isinstance(attr, type) and
                    attr.__module__ == module_name and
                    not attr_name.startswith("_")  # исключаем приватные
            ):
                classes[attr_name] = attr

    return classes

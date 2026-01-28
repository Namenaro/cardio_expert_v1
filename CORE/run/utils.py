import os
import importlib.util
import sys
from pathlib import Path
from typing import Dict, Type, List

from CORE.constants import EPSILON_FOR_DUBLES


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


def delete_similar_points(points_coords: List[float]) -> None:
    """
    Удаляет из списка координат points_coords точки, которые находятся ближе друг к другу,
    чем EPSILON_FOR_DUBLES. В результате оставшиеся точки попарно удалены друг от друга
    на расстояние >= EPSILON_FOR_DUBLES.

    :param points_coords: список координат точек (изменяется напрямую)
    """
    if len(points_coords) <= 1:
        return  # Ничего удалять не нужно

    # Сортируем координаты
    points_coords.sort()

    # Список для хранения индексов точек, которые нужно оставить
    keep_indices = [0]  # Всегда оставляем первую точку

    last_kept_coord = points_coords[0]

    for i in range(1, len(points_coords)):
        current_coord = points_coords[i]
        # Если текущая точка достаточно удалена от последней сохранённой — оставляем её
        if abs(current_coord - last_kept_coord) >= EPSILON_FOR_DUBLES:
            keep_indices.append(i)
            last_kept_coord = current_coord

    # Перестраиваем исходный список, оставляя только нужные точки
    points_coords[:] = [points_coords[i] for i in keep_indices]

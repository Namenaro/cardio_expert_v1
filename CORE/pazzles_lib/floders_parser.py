import ast
from pathlib import Path
from typing import List, Tuple

from CORE.db_dataclasses.base_class import BaseClass, CLASS_TYPES
from CORE.pazzles_lib.class_parser import ClassParser


class FoldersParser:
    """Парсер для обработки классов паззлов"""

    def __init__(self, base_package: str = "pazzles_lib"):
        self.base_package = base_package
        self.class_parser = ClassParser()

    def parse_all_folders(self) -> Tuple[List[BaseClass], List[BaseClass], List[BaseClass], List[BaseClass]]:
        """
        Парсит все классы в четырех папках и возвращает 4 списка

        Returns:
            Tuple с четырьмя списками: (pc_list, hc_list, ps_list, sm_list)
        """
        pc_list = self._parse_folder("PC", CLASS_TYPES.PC)
        hc_list = self._parse_folder("HC", CLASS_TYPES.HC)
        ps_list = self._parse_folder("PS", CLASS_TYPES.PS)
        sm_list = self._parse_folder("SM", CLASS_TYPES.SM)

        return pc_list, hc_list, ps_list, sm_list

    def _parse_folder(self, folder_name: str, class_type: CLASS_TYPES) -> List[BaseClass]:
        """
        Парсит все классы в указанной папке

        Args:
            folder_name: Имя папки (PC, HC, PS, SM)
            class_type: Тип классов в этой папке

        Returns:
            Список распарсенных классов
        """
        classes_list = []
        folder_path = self._get_folder_path(folder_name)

        if not folder_path.exists():
            print(f"Предупреждение: папка {folder_path} не найдена")
            return classes_list

        # Ищем все Python файлы в папке (кроме __init__.py)
        python_files = [f for f in folder_path.glob("*.py") if f.name != "__init__.py"]

        for file_path in python_files:
            try:
                class_info = self._parse_file(file_path, class_type)
                if class_info:
                    classes_list.append(class_info)
            except Exception as e:
                print(f"    ✗ Ошибка при парсинге файла {file_path}: {e}")

        return classes_list

    def _get_folder_path(self, folder_name: str) -> Path:
        """Возвращает полный путь к папке с классами"""
        return Path(__file__).parent / folder_name

    def _parse_file(self, file_path: Path, class_type: CLASS_TYPES) -> BaseClass:
        """
        Парсит один файл и возвращает информацию о классе

        Args:
            file_path: Путь к файлу
            class_type: Тип класса (из названия папки)

        Returns:
            BaseClass с заполненной информацией
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        tree = ast.parse(content)

        # Ищем все классы в файле (на случай, если их несколько)
        class_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_nodes.append(node)

        if not class_nodes:
            raise ValueError(f"В файле {file_path} не найдено классов")

        # Парсим первый найденный класс
        first_class = class_nodes[0]
        original_class = self.class_parser.parse_class(first_class)

        # Создаем расширенный класс с типом
        base_class = BaseClass(
            name=original_class.name,
            comment=original_class.comment,
            type=class_type.value,
            constructor_arguments=original_class.constructor_arguments,
            input_params=original_class.input_params,
            input_points=original_class.input_points,
            output_params=original_class.output_params
        )

        return base_class


def print_detailed_summary(pc_list: List[BaseClass], hc_list: List[BaseClass],
                           ps_list: List[BaseClass], sm_list: List[BaseClass]) -> None:
    """
    Подробно распечатывает информацию о всех найденных классах
    """

    total_classes = len(pc_list) + len(hc_list) + len(ps_list) + len(sm_list)
    print(f"Всего найдено классов: {total_classes}\n")

    categories = [
        ("PC", pc_list),
        ("HC", hc_list),
        ("PS", ps_list),
        ("SM", sm_list)
    ]

    for category_name, category_list in categories:
        if category_list:
            print(f"{'=' * 40}")
            print(f"{category_name} КЛАССЫ ({len(category_list)}):")
            print(f"{'=' * 40}")
            for i, class_info in enumerate(category_list, 1):
                print(f"[{i}] {class_info}")
                print()  # Пустая строка между классами


# Пример использования
if __name__ == "__main__":
    # Парсим все 4 папки
    folders_parser = FoldersParser("pazzles_lib")
    pc_list, hc_list, ps_list, sm_list = folders_parser.parse_all_folders()

    # Выводим сводку
    print_detailed_summary(pc_list, hc_list, ps_list, sm_list)

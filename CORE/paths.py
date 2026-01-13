"""
Конфигурационный файл с путями к данным и функцией инициализации директорий.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Основая база данных, заполненная в DA
DB_NAME = "test_database.db"
DB_PATH = os.path.join(BASE_DIR, "data", DB_NAME)

# Папка с json-файлами датасетов экземплярв форм, заполняемых в Datagen
EXEMPLARS_DATASETS_PATH = os.path.join(BASE_DIR, "data", "forms_datasets")

# Внешние датасеты
LUDB_JSON_PATH = os.path.join(BASE_DIR, "data", "ecg_data_200.json")


def create_directories():
    """Создаёт директории, если их нет."""
    directories = [
        os.path.dirname(DB_PATH),
        EXEMPLARS_DATASETS_PATH

    ]
    for dir_path in directories:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

# Константы приложения

import os

# Получаем абсолютный путь к папке, где находится paths.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Основая база данных, заполненная в DA
DB_NAME = "test_database.db"
DB_PATH = os.path.join(BASE_DIR, "data", DB_NAME)

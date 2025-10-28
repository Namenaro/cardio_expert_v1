# Константы приложения

import os

# Получаем абсолютный путь к папке, где находится settings.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Константы приложения
DB_PATH = os.path.join(BASE_DIR, "test_database.db")
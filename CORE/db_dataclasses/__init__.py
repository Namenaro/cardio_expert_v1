from CORE.db_dataclasses.form import Form
from CORE.db_dataclasses.point import Point
from CORE.db_dataclasses.parameter import Parameter
from CORE.db_dataclasses.track import Track
from CORE.db_dataclasses.step import Step

from CORE.db_dataclasses.base_pazzle import *
from CORE.db_dataclasses.base_class import *
from CORE.db_dataclasses.classes_to_pazzles_helpers import *


import sys

# Собираем all полуавтоматически
__all__ = ['Form', 'Point', 'Parameter', 'Track', 'Step', 'BaseClass']

# Получаем текущий модуль
current_module = sys.modules[__name__]

# Добавляем все имена, которые начинаются с заглавной буквы
for attr_name in dir(current_module):
    if attr_name[0].isupper() and not attr_name.startswith('_'):
        if attr_name not in __all__:
            __all__.append(attr_name)

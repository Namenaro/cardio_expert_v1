from CORE.main_entities.form import Form
from CORE.main_entities.step import Step
from CORE.main_entities.track import Track
from CORE.main_entities.point import Point
from CORE.main_entities.parameter import Parameter

from CORE.pazzles_lib.SM_base import SM
from CORE.pazzles_lib.PS_base import PS
from CORE.pazzles_lib.PC_base import PC
from CORE.pazzles_lib.HC_base import HC

#---------------------------------------------------------------------------
# ОСВНОЙ МЕТОД: прочитать форму из БД
#---------------------------------------------------------------------------
def read_form(form_name)->Form:
    # кинуть исключение, если нет
    pass

#---------------------------------------------------------------------------
# Вспомогательные методы: чтение составляющих элементов формы
#---------------------------------------------------------------------------
def read_param_by_id(param_id)->Parameter:
    # кинуть исключение, если нет
    pass

def read_point_by_id(point_id)->Point:
    # кинуть исключение, если нет
    pass

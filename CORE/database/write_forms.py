from CORE.main_entities.form import Form
from CORE.main_entities.step import Step
from CORE.main_entities.track import Track
from CORE.pazzles_lib.SM_base import SM
from CORE.pazzles_lib.PS_base import PS
from CORE.pazzles_lib.PC_base import PC
from CORE.pazzles_lib.HC_base import HC

#---------------------------------------------------------------------------
# ТРИ ОСНОВНЫХ МЕТОДА: добавить нову форму, удалить форму, изменить существующую форму
#---------------------------------------------------------------------------
def add_new_form(form:Form):
    # кинуть исключение, если имя новой формы неуникально
    pass # return id добавленной формы

def delete_form(form_name: str):
    # Каскадно удаляем форму с именем "form_name" (т.е. шаги, точки, параметры, объекты всех классов(но не классы)
    # кинуть исключение, если такой формы нет
    pass #ничего не возвращаем

def change_existing_form(form_name, form:Form):
    delete_form(form_name)
    add_new_form(form)


#---------------------------------------------------------------------------
# Вспомогательные методы: добавление составляющих элементов формы
#---------------------------------------------------------------------------
def add_new_point(name, comment, form_id):
    pass  # return id точки

def add_new_param(name, comment, form_id):
    pass  # return id параметра

def add_new_step_to_form(form_id, step_num, step:Step):
    pass # return id добавленного шага

def add_new_track_to_step(step_id, track:Track):
    pass  # return id добавленного трека

def add_new_SM_to_track(track_id, num_in_track, SM:SM):
    pass # тут ничего не возвращается

def add_new_PS_to_track(track_id, num_in_track, PS:PS):
    pass # тут ничего не возвращается

def add_new_PC_to_track(track_id, num_in_track, PC:PC):
    pass # тут ничего не возвращается

def add_new_HC_to_track(track_id, num_in_track, HC:HC):
    pass # тут ничего не возвращается
from CORE.dataclasses import Form, SMClassInfo, PSClassInfo, PCClassInfo, HCClassInfo

from typing import List, Optional

class DBWrapperForDoctor:
    def __init__(self):
        pass

    def get_all_forms_names(self)->List[str]:
        """ Вернуть список всех имен формы (см. form.name)"""
        pass

    def read_form_by_name(self, form_name:str)->Optional[Form]:
        """ По имени формы из form.name десериализовать объект Form. Если такой формы не найдено, вернуть None"""
        pass

    def delete_form(self, form_name):
        """Удалить форму с таким именем из БД. Если ее там не было, то кинуть исключение.
         При удалении формы нужно удалить все связанные с ней точки и параметры, шаги, треки, объекты всех классов."""
        pass

    def add_form(self, form:Form):
        """ Добавить форму в БД, если не удается - кинуть исключение"""
        pass


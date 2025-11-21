from import QObject

from CORE.db_dataclasses import Form
from CORE.database.forms_service_read import FormsServiceRead
from CORE.database.forms_service_write import FormsServiceWrite
from CORE.database.db_manager import DBManager


from typing import List


class FormController(QObject):
    def __init__(self,  db: 'DBManager'):
        self.old_form = None # Это версия, соответсвующая предыдущей валидной транзакции (т.е. перед редактированием)
        self.current_form = None # Это редактируемая. В какой то момент для нее мы вызываем старт транзакции
        self.deep_copy_current_form = None # Это чисто на время хода транзакции, временная копия редактируемой формы, живущая от начала транзакции до роллбека или успеха

        self.reader = FormsServiceRead(db)
        self.writer = FormsServiceWrite(db)

    # Общие

    def get_all_forms_names(self)->List[str]:
        forms = self.reader.get_all_form_entries()
        forms_names = [form.name for form in forms]
        return forms_names

    def start_with_new_form(self):
        self.form = Form()

    def load_form(self, form_id:int)->Form:
        pass

    def create_copy_of_form(self, form_id)->Form:
        form = self.load_form(form_id)
        form.clear_all_ids()
        return form

    def delete_form(self, form_id):
        pass

    #Точки и параметры
    def update_point(self, point_id):
        pass

    def update_parameter(self, parameter_id):
        pass

    def delete_point(self, point_id):
        pass

    def delete_parameter(self, parameter_id):
        pass

    def add_new_point(self, point):
        # не только добавили, но и id поменяли
        pass

    def add_new_parameter(self, parameter):
        # не только добавили, но и id поменяли
        pass

    # Пазлы:
    def add_new_pazzle_HC_PC(self, obj):
        # не только добавляем, но и кучу айдишникв в глубокую копию
        pass

    def update_pazzle(self, obj_id):
        # счачала лезем в старый вариант этого объекта (до запуска редактора!)
        # потом лезем в текущий вариант (после закрытия редактора)
        # сраваниваем, что именно изменилось и в соотв репозиториях вызываем нужные ubdate\delete\add
        pass

    def delete_pazzle(self, obj_id):
        pass

    def add_new_pazzle_SM_PS(self, obj, track_id, num_in_track):
        # не только добавляем, но и кучу айдишникв в глубокую копию
        pass

    # Шаги:
    def add_step(self, step):
        # не только добавляем, но и кучу айдишникв в глубокую копию
        pass

    def delete_step(self, step_id):
        pass




    def update_track(self):






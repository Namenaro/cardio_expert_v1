from CORE.dataclasses import Form
from CORE.database import DBWrapperForDoctor

from typing import List

class AppModel:
    def __init__(self):
        self.form:Form = None
        self.db_wrapper = DBWrapperForDoctor()
        # TODO self.simulator = None

    def get_all_forms_names(self)->List[str]:
        return self.db_wrapper.get_all_forms_names()

    def create_new_form(self):
        pass

    def load_form_by_name(self, form_name:str):
        self.form = self.db_wrapper.deserialize_form_by_name(form_name)

    def delete_form(self, form_name):
        self.db_wrapper.delete_form(form_name)

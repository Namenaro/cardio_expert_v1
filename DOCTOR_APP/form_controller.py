from CORE.dataclasses import Form
from CORE.database import FormsRepo

from typing import List, Optional

class FormController:
    def __init__(self):
        self.form:Optional[Form] = None
        self.db_wrapper = FormsRepo()
        # TODO self.simulator = None

    def get_all_forms_names(self):
        return self.db_wrapper.get_all_forms_names()

    def create_new_form(self):
        pass

    def load_form(self, form_id:int):
        self.form = self.db_wrapper.get_form(form_id)

    def delete_form(self, form_id):
        self.db_wrapper.delete_form(form_id)

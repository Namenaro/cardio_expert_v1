from CORE.dataclasses import Form
from CORE.database import FormsRepo

from typing import List, Optional

class FormController:
    def __init__(self, forms_repository:FormsRepo):
        self.form:Optional[Form] = None
        self.db = forms_repository
        # TODO self.simulator = None

    def get_all_forms(self)->List[Form]:
        return self.db.get_all_forms_summaries()

    def start_with_new_form(self):
        self.form = Form()

    def load_form(self, form_id:int):
        self.form = self.db.get_form(form_id)

    def delete_form(self, form_id):
        self.db.delete_form(form_id)

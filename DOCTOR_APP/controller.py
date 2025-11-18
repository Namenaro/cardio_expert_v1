from CORE.db_dataclasses import Form
from CORE.database.forms_service_read import FormsServiceRead
from CORE.database.forms_service_write import FormsServiceWrite
from CORE.database.db_manager import DBManager


from typing import List, Optional

class FormController:
    def __init__(self,  db: 'DBManager'):
        self.form:Optional[Form] = None
        self.reader = FormsServiceRead(db)
        self.writer = FormsServiceWrite(db)
        # TODO self.simulator = None

    def get_all_forms_summaries(self)->List[str]:
        forms = self.reader.get_all_form_entries()
        forms_names = [form.name for form in forms]
        return forms_names

    def start_with_new_form(self):
        self.form = Form()

    def load_form(self, form_id:int):
        pass

    def delete_form(self, form_id):
        pass

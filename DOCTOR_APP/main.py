from app_model import AppModel

from typing import Optional, List

def run_start_dialog(forms_names:List[str])-> Optional[str]:
    pass

if __name__ == "__main__":
    app_model = AppModel()
    forms_names = app_model.get_all_forms_names()

    name_selected = run_start_dialog(forms_names)

    if name_selected is None:
        app_model.create_new_form()
    else:
        app_model.load_form_by_name(name_selected)


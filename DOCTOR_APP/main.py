from form_controller import FormController

from typing import Optional, List

def run_start_dialog(forms_names:List[str])-> Optional[str]:
    pass

if __name__ == "__main__":
    controller = FormController()
    forms_names = controller.get_all_forms_names()

    name_selected = run_start_dialog(forms_names)

    if name_selected is None:
        controller.create_new_form()
    else:
        controller.load_form_by_name(name_selected)


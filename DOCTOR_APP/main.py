from form_controller import FormController
from start_dialog import run_start_dialog
from CORE.db.db_manager import DBManager

from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":

    db = DBManager()
    controller = FormController(db)
    app = QApplication(sys.argv)
    
    forms_names = controller.get_all_forms_summaries()
    selected_form = run_start_dialog(forms_names)


    if selected_form is None:
        controller.start_with_new_form()
    else:
        print(f"\nРезультат: Пользователь выбрал существующую форму: '{selected_form}'")

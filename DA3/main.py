from DA3.controller import Contoller
from CORE.db_dataclasses import Form
from DA3.start_dialog import select_form_from_dialog
from DA3.main_form import MainForm


from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QApplication,
                               QListWidget, QPushButton, QListWidgetItem)
from PySide6.QtCore import Qt

import sys
from typing import List, Optional


def main():
    app = QApplication(sys.argv)

    controller = Contoller()

    # Показываем диалог выбора формы
    forms = controller.get_all_forms_summaries()
    form_id, create_new = select_form_from_dialog(forms)
    if form_id is None and not create_new:
        return

    # Показываем главную форму
    main_window = MainForm(form_id, create_new)
    main_window.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()






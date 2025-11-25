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
    """Главная функция приложения"""
    app = QApplication(sys.argv)

    # Тестовые данные форм
    forms = [
        Form(1, "Форма заказа", "Для оформления заказов"),
        Form(2, "Форма клиента", "Данные клиентов"),
        Form(3, "Форма товара", "Информация о товарах")
    ]

    # Показываем диалог выбора формы
    form_id, create_new = select_form_from_dialog(forms)

    # Если диалог закрыт через крестик - выходим
    if form_id is None and not create_new:
        print("Диалог закрыт через крестик - приложение завершено")
        return  # Завершаем функцию main

    # Показываем главную форму
    main_window = MainForm(form_id, create_new)
    main_window.show()

    # Запускаем главный цикл приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main()






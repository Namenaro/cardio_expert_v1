from CORE.db_dataclasses import Form

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QListWidget, QPushButton, QListWidgetItem,
                               QLabel, QApplication)

from PySide6.QtCore import Qt
from typing import List, Optional, Tuple


def select_form_from_dialog(forms: List[Form]) -> Tuple[Optional[int], bool]:
    dialog = FormSelectionDialog(forms)

    if dialog.exec() == QDialog.Accepted:
        return dialog.get_selection_result()
    else:
        # Диалог закрыт через крестик
        return None, False


class FormSelectionDialog(QDialog):
    def __init__(self, forms: List[Form], parent=None):
        super().__init__(parent)
        self.forms = forms
        self.selected_form_id = None
        self.create_new_form = False

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Выбор формы")
        self.setModal(True)
        self.resize(400, 500)

        # Основной layout
        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel("Выберите существующую форму или создайте новую:")
        layout.addWidget(title_label)

        # ListWidget для отображения списка форм
        self.list_widget = QListWidget()

        # Заполняем список формами
        for form in self.forms:
            item_text = f"{form.name}"
            if form.comment:
                item_text += f" - {form.comment}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, form.id)  # Сохраняем id в данных элемента
            self.list_widget.addItem(item)

        # Выделяем первый элемент по умолчанию
        if self.forms:
            self.list_widget.setCurrentRow(0)

        layout.addWidget(self.list_widget)

        # Layout для кнопок
        button_layout = QHBoxLayout()

        # Кнопка "Выбрать"
        self.select_button = QPushButton("Выбрать")
        self.select_button.clicked.connect(self.accept_selection)

        # Кнопка "Создать новую форму"
        self.create_button = QPushButton("Создать новую форму")
        self.create_button.clicked.connect(self.create_new_form_action)

        button_layout.addWidget(self.select_button)
        button_layout.addWidget(self.create_button)

        layout.addLayout(button_layout)

        # Двойной клик по элементу тоже выбирает его
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)

    def accept_selection(self):
        """Обработка выбора существующей формы"""
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_form_id = current_item.data(Qt.UserRole)
            self.create_new_form = False
            self.accept()

    def create_new_form_action(self):
        """Обработка создания новой формы"""
        self.selected_form_id = None
        self.create_new_form = True
        self.accept()

    def get_selection_result(self) -> tuple[Optional[int], bool]:
        """
        Возвращает результат выбора

        Returns:
            tuple: (form_id, create_new)
            - form_id: ID выбранной формы или None
            - create_new: True если нажата кнопка создания новой формы
        """
        return self.selected_form_id, self.create_new_form


# Пример использования
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    # Тестовые данные
    forms = [
        Form(1, "Форма 1", "Коммент 1", "", ""),
        Form(2, "Форма 2", "Коммент 2", "", ""),
        Form(3, "Форма 3", "Коммент 3", "", "")
    ]

    form_id, create_new = select_form_from_dialog(forms)

    if create_new:
        print("Пользователь выбрал создание новой формы")
    elif form_id is not None:
        print(f"Выбрана форма с ID: {form_id}")
    else:
        print("Диалог закрыт через крестик")

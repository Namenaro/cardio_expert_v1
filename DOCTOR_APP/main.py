import sys
from typing import List, Optional

from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
    QListWidget, QPushButton, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

def run_start_dialog(forms_names: List[str]) -> Optional[str]:

    class StartDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Начало работы")
            self.setFixedSize(450, 350)
            
            # стандартные кнопки управления окном
            self.setWindowFlags(
                Qt.Window |
                Qt.WindowMinimizeButtonHint |
                Qt.WindowMaximizeButtonHint |
                Qt.WindowCloseButtonHint
            )
            
            # хранение результата и состояний
            self.result: Optional[str] = None
            self._selected_form: Optional[str] = None
            self.current_state: str = ''

            
            self.create_button = QPushButton("Создать новую форму")
            self.select_button = QPushButton("Выбрать существующую форму")
            self.forms_list = QListWidget()
            self.forms_list.addItems(forms_names)
            self.confirm_label = QLabel()
            self.ok_button = QPushButton("OK")
            self.cancel_button = QPushButton("Cancel")

            #внешний вид
            button_font = QFont()
            button_font.setPointSize(12)
            self.create_button.setFont(button_font)
            self.create_button.setFixedHeight(50)
            self.select_button.setFont(button_font)
            self.select_button.setFixedHeight(50)

            # сбор интерфейса
            main_layout = QVBoxLayout(self)
            confirm_layout = QHBoxLayout()
            confirm_layout.addStretch()
            confirm_layout.addWidget(self.cancel_button)
            confirm_layout.addWidget(self.ok_button)

            main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            main_layout.addWidget(self.create_button)
            main_layout.addWidget(self.select_button)
            main_layout.addWidget(self.forms_list)
            main_layout.addWidget(self.confirm_label)
            main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
            main_layout.addLayout(confirm_layout)
            
            self.create_button.clicked.connect(self.on_create_new)
            self.select_button.clicked.connect(self.on_select_existing_toggle) # ### ИЗМЕНЕНИЕ 2: Привязываем к новой функции-переключателю
            self.forms_list.itemClicked.connect(self.on_item_selected)
            self.ok_button.clicked.connect(self.on_confirm)
            self.cancel_button.clicked.connect(self.on_cancel)

            self.set_state('initial')

        def set_state(self, state: str):
            self.current_state = state
            
            if state == 'initial':
                self.create_button.show()
                self.select_button.show()
                self.forms_list.hide()
                self.confirm_label.hide()
                self.ok_button.hide()
                self.cancel_button.hide()
            elif state == 'selection':
                self.create_button.show()
                self.select_button.show()
                self.forms_list.show()
                self.confirm_label.hide()
                self.ok_button.hide()
                self.cancel_button.hide()
            elif state == 'confirmation':
                self.create_button.hide()
                self.select_button.hide()
                self.forms_list.hide()
                self.confirm_label.show()
                self.ok_button.show()
                self.cancel_button.show()
        
        def on_select_existing_toggle(self):
            if self.current_state == 'initial':
                self.set_state('selection') # показываем список
            elif self.current_state == 'selection':
                self.set_state('initial') # скрываем список

        def on_create_new(self):
            self.result = None
            self.accept()

        def on_item_selected(self, item):
            self._selected_form = item.text()
            confirm_text = f'<b><font size="5" color="green">✓</font> <font size="5">{self._selected_form}</font></b>'
            self.confirm_label.setText(confirm_text)
            self.confirm_label.setAlignment(Qt.AlignCenter)
            self.set_state('confirmation')

        def on_confirm(self):
            self.result = self._selected_form
            self.accept()

        def on_cancel(self):
            self._selected_form = None
            self.set_state('initial')

    dialog = StartDialog()
    dialog.exec()
    return dialog.result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    test_forms_list = ["QR_form", "RS_form", "QRS_form", "R_form"] #пример форм

    print("Запускаем стартовый диалог...")
    selected_form = run_start_dialog(test_forms_list)
    print("Диалог закрыт.")

    if selected_form is None:
        print("\nРезультат: Пользователь выбрал 'Создать новую форму' (или закрыл окно).")
    else:
        print(f"\nРезультат: Пользователь выбрал существующую форму: '{selected_form}'")

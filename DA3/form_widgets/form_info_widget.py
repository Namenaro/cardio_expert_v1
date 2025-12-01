from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PySide6.QtCore import Qt
from CORE.db_dataclasses import Form
from DA3 import app_signals


class FormInfoWidget(QWidget):
    """Виджет основной информации о форме"""

    def __init__(self):
        super().__init__()
        self._form: Optional[Form] = None
        self.setup_ui()

    def setup_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel("Основная информация о форме")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Grid layout для отображения информации
        self.info_grid = QGridLayout()
        self.info_grid.setSpacing(5)
        self.info_grid.setContentsMargins(5, 5, 5, 5)

        # ID формы
        id_label = QLabel("ID формы:")
        id_label.setStyleSheet("font-weight: bold;")
        self.id_value_label = QLabel("не задан")
        self.id_value_label.setStyleSheet("color: #666; padding-left: 10px;")

        # Имя формы
        name_label = QLabel("Имя формы:")
        name_label.setStyleSheet("font-weight: bold;")
        self.name_value_label = QLabel("не задано")
        self.name_value_label.setStyleSheet("color: #666; padding-left: 10px;")

        # Комментарий
        comment_label = QLabel("Комментарий:")
        comment_label.setStyleSheet("font-weight: bold;")
        self.comment_value_label = QLabel("не задан")
        self.comment_value_label.setStyleSheet("color: #666; padding-left: 10px;")
        self.comment_value_label.setWordWrap(True)

        # Добавляем элементы в grid
        row = 0
        self.info_grid.addWidget(id_label, row, 0, Qt.AlignmentFlag.AlignRight)
        self.info_grid.addWidget(self.id_value_label, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        self.info_grid.addWidget(name_label, row, 0, Qt.AlignmentFlag.AlignRight)
        self.info_grid.addWidget(self.name_value_label, row, 1, Qt.AlignmentFlag.AlignLeft)
        row += 1

        self.info_grid.addWidget(comment_label, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.info_grid.addWidget(self.comment_value_label, row, 1, Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(self.info_grid)

        # Пустое пространство (растягивающийся элемент)
        main_layout.addStretch()

        # Кнопка редактирования
        self.edit_button = QPushButton("Редактировать основную информацию")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        self.edit_button.setEnabled(False)  # По умолчанию выключена, пока форма не установлена
        self.edit_button.setMinimumHeight(40)
        self.edit_button.setStyleSheet("""
            QPushButton {
                font-weight: bold;
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton:hover:!disabled {
                background-color: #45a049;
            }
        """)
        main_layout.addWidget(self.edit_button)

        # Общий стиль виджета
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
        """)

    def reset_form(self, form: Form) -> None:
        """Установить новую форму для отображения"""
        self._form = form
        self.refresh()

    def refresh(self) -> None:
        """Обновить отображение информации о форме"""
        if self._form is None:
            # Очищаем все поля
            self.id_value_label.setText("не задан")
            self.name_value_label.setText("не задано")
            self.comment_value_label.setText("не задан")

            # Выключаем кнопку редактирования
            self.edit_button.setEnabled(False)
            return

        # Обновляем основную информацию
        form_id = str(self._form.id) if self._form.id is not None else "не задан"
        self.id_value_label.setText(form_id)
        self.name_value_label.setText(self._form.name or "не задано")
        self.comment_value_label.setText(self._form.comment or "не задан")

        # Включаем кнопку редактирования
        self.edit_button.setEnabled(True)

    def on_edit_clicked(self) -> None:
        """Обработчик нажатия кнопки редактирования"""
        if self._form is not None:
            # Испускаем сигнал с формой и ссылкой на себя
            app_signals.request_main_info_redactor.emit(self._form, self)

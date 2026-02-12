from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QFrame
)
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from CORE.db_dataclasses import Form
from DA3 import app_signals
import os


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

        # Картинка
        image_label = QLabel("Изображение:")
        image_label.setStyleSheet("font-weight: bold;")

        # Контейнер для изображения
        self.image_frame = QFrame()
        self.image_frame.setFrameShape(QFrame.Shape.Box)
        self.image_frame.setLineWidth(1)
        self.image_frame.setStyleSheet("background-color: #f0f0f0; border: 1px solid #cccccc;")
        self.image_frame.setFixedSize(200, 150)  # Фиксированный размер для картинки

        # Layout для фрейма с картинкой
        self.image_layout = QVBoxLayout(self.image_frame)
        self.image_layout.setContentsMargins(5, 5, 5, 5)
        self.image_layout.setSpacing(0)

        # Метка для изображения
        self.image_display_label = QLabel()
        self.image_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display_label.setFixedSize(190, 140)  # Немного меньше чем фрейм

        # Текст плейсхолдера
        self.placeholder_label = QLabel("Изображение\nне загружено")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color: #999999; font-size: 11px;")
        self.placeholder_label.setWordWrap(True)

        self.image_layout.addWidget(self.image_display_label)
        self.image_layout.addWidget(self.placeholder_label)

        # Сначала показываем плейсхолдер
        self.placeholder_label.setVisible(True)
        self.image_display_label.setVisible(False)

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
        row += 1

        # Картинка занимает две строки для выравнивания по вертикали
        self.info_grid.addWidget(image_label, row, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.info_grid.addWidget(self.image_frame, row, 1, 2, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(self.info_grid)

        # Пустое пространство (растягивающийся элемент)
        main_layout.addStretch()

        # Кнопка редактирования
        self.edit_button = QPushButton("Редактировать основную информацию")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        self.edit_button.setEnabled(False)  # По умолчанию выключена, пока форма не установлена
        self.edit_button.setMinimumHeight(40)

        main_layout.addWidget(self.edit_button)

        # Кнопка удаления формы
        self.delete_button = QPushButton("Удалить форму")
        self.delete_button.setStyleSheet("""
            background-color: #ff4444;
            color: white;
            font-weight: bold;
            border: none;
            padding: 10px;
            border-radius: 5px;
        """)
        self.delete_button.setMinimumHeight(40)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setEnabled(False)  # По умолчанию выключена, пока форма не установлена

        main_layout.addWidget(self.delete_button)

        self.setStyleSheet("background-color: #e6e6ff;")

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

            # Показываем плейсхолдер для изображения
            self._show_placeholder("Форма не выбрана")

            # Выключаем кнопки редактирования и удаления
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return

        # Обновляем основную информацию
        form_id = str(self._form.id) if self._form.id is not None else "не задан"
        self.id_value_label.setText(form_id)
        self.name_value_label.setText(self._form.name or "не задано")
        self.comment_value_label.setText(self._form.comment or "не задан")

        # Обновляем изображение
        self._update_image_display()

        # Включаем кнопки редактирования и удаления
        self.edit_button.setEnabled(True)
        self.delete_button.setEnabled(True)

    def _update_image_display(self):
        """Обновить отображение изображения формы"""
        if not self._form or not self._form.path_to_pic:
            self._show_placeholder("Изображение\nне загружено")
            return

        image_path = self._form.path_to_pic

        # Проверяем, существует ли файл
        if not os.path.exists(image_path):
            self._show_placeholder(f"Файл не найден:\n{os.path.basename(image_path)}")
            return

        try:
            # Загружаем изображение
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                self._show_placeholder("Неверный формат\nизображения")
                return

            # Масштабируем изображение для отображения
            scaled_pixmap = pixmap.scaled(
                self.image_display_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # Показываем изображение
            self.image_display_label.setPixmap(scaled_pixmap)
            self.image_display_label.setVisible(True)
            self.placeholder_label.setVisible(False)

        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            self._show_placeholder("Ошибка загрузки\nизображения")

    def _show_placeholder(self, text: str = "Изображение\nне загружено"):
        """Показать плейсхолдер вместо изображения"""
        self.placeholder_label.setText(text)
        self.placeholder_label.setVisible(True)
        self.image_display_label.setVisible(False)

        # Очищаем предыдущее изображение
        self.image_display_label.setPixmap(QPixmap())

    @Slot()
    def on_edit_clicked(self) -> None:
        if self._form is not None:
            app_signals.form.request_main_info_redactor.emit(self._form)

    @Slot()
    def on_delete_clicked(self) -> None:
        """Обработчик нажатия кнопки удаления формы"""
        if self._form is None:
            return

        from PySide6.QtWidgets import QMessageBox

        # Показываем диалоговое окно с подтверждением
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Удалить форму?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Эмит сигнала на удаление формы из БД
            app_signals.form.db_delete_form.emit(self._form)

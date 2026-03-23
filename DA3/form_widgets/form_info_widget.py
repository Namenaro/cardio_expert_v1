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

from DA3.base_widget import BaseWidget


class FormInfoWidget(BaseWidget):
    """Виджет основной информации о форме"""

    def __init__(self):
        super().__init__()
        self._form: Optional[Form] = None
        self.setup_ui()
        # Применяем стили (теперь они будут работать благодаря установленным objectName и property)
        self.apply_styles("common.qss", "form_info_widget.qss")

    def setup_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок - добавляем objectName для стилизации
        title_label = QLabel("Основная информация о форме")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("mainTitle")  # <-- Добавлено для CSS
        main_layout.addWidget(title_label)

        # Карточка с информацией - создаем контейнер для группировки
        self.info_card = QFrame()
        self.info_card.setObjectName("infoCard")  # <-- Добавлено для CSS
        self.info_card.setProperty("class", "card")  # <-- Для общих стилей карточек
        card_layout = QVBoxLayout(self.info_card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(10)

        # Grid layout для отображения информации
        self.info_grid = QGridLayout()
        self.info_grid.setSpacing(10)
        self.info_grid.setContentsMargins(0, 0, 0, 0)

        # ID формы - добавляем property для стилизации
        id_label = QLabel("ID формы:")
        id_label.setProperty("class", "fieldLabel")  # для CSS
        id_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.id_value_label = QLabel("не задан")
        self.id_value_label.setProperty("class", "valueLabel")  # для CSS

        # Имя формы
        name_label = QLabel("Имя формы:")
        name_label.setProperty("class", "fieldLabel")  # для CSS
        name_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_value_label = QLabel("не задано")
        self.name_value_label.setProperty("class", "valueLabel")  # для CSS

        # Комментарий
        comment_label = QLabel("Комментарий:")
        comment_label.setProperty("class", "fieldLabel")  # для CSS
        comment_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.comment_value_label = QLabel("не задан")
        self.comment_value_label.setProperty("class", "valueLabel")  # для CSS
        self.comment_value_label.setWordWrap(True)

        # Картинка
        image_label = QLabel("Изображение:")
        image_label.setProperty("class", "fieldLabel")  # для CSS
        image_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Контейнер для изображения - добавляем objectName
        self.image_frame = QFrame()
        self.image_frame.setObjectName("imageFrame")  # для CSS
        self.image_frame.setFixedSize(200, 150)

        # Layout для фрейма с картинкой
        self.image_layout = QVBoxLayout(self.image_frame)
        self.image_layout.setContentsMargins(5, 5, 5, 5)
        self.image_layout.setSpacing(0)

        # Метка для изображения
        self.image_display_label = QLabel()
        self.image_display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display_label.setFixedSize(190, 140)

        # Текст плейсхолдера - добавляем objectName
        self.placeholder_label = QLabel("Изображение\nне загружено")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setObjectName("placeholderLabel")  # для CSS
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

        card_layout.addLayout(self.info_grid)
        main_layout.addWidget(self.info_card)

        # Пустое пространство (растягивающийся элемент)
        main_layout.addStretch()

        # Кнопка редактирования - добавляем objectName
        self.edit_button = QPushButton("Редактировать основную информацию")
        self.edit_button.setObjectName("editButton")  # для CSS
        self.edit_button.clicked.connect(self.on_edit_clicked)
        self.edit_button.setEnabled(False)
        self.edit_button.setMinimumHeight(40)

        main_layout.addWidget(self.edit_button)

        # Кнопка удаления формы - добавляем objectName
        self.delete_button = QPushButton("Удалить форму")
        self.delete_button.setObjectName("deleteButton")  # для CSS
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.delete_button.setEnabled(False)
        self.delete_button.setMinimumHeight(40)

        main_layout.addWidget(self.delete_button)


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
            self._show_placeholder("\nФорма не выбрана")

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
            self._show_placeholder("\nИзображение\nне загружено")
            return

        image_path = self._form.path_to_pic

        # Проверяем, существует ли файл
        if not os.path.exists(image_path):
            self._show_placeholder(f"\nФайл не найден:\n{os.path.basename(image_path)}")
            return

        try:
            # Загружаем изображение
            pixmap = QPixmap(image_path)

            if pixmap.isNull():
                self._show_placeholder("\nНеверный формат\nизображения")
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
            self._show_placeholder("\nОшибка загрузки\nизображения")

    def _show_placeholder(self, text: str = "\nИзображение\nне загружено"):
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

        # Стилизованное диалоговое окно
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Вы действительно хотите удалить эту форму?")
        msg_box.setInformativeText("Это действие нельзя будет отменить.")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            app_signals.form.db_delete_form.emit(self._form)
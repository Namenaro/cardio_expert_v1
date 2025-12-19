from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QFileDialog,
    QComboBox, QRadioButton, QGroupBox, QApplication
)
from DA3.redactors_widgets.base_editor import BaseEditor
from DA3 import app_signals
from CORE.db_dataclasses import *
from copy import deepcopy


class StepInfoEditor(BaseEditor):
    """Редактор основной информации о шаге"""

    def __init__(self, parent: QWidget, step: Step, points: List[Point]):
        # Сначала сохраняем points, чтобы они были доступны в setup_ui родителя
        self._points = points
        # Теперь вызываем родительский __init__, который запустит setup_ui
        super().__init__(parent, step)
        self.setWindowTitle("Редактирование параметра")
        self.resize(400, 300)

        # Подключаем обработчики переключения радио-кнопок
        self.left_point_radio.toggled.connect(self._on_left_radio_toggled)
        self.right_point_radio.toggled.connect(self._on_right_radio_toggled)

    def _on_left_radio_toggled(self, checked: bool):
        """Обработчик переключения радио-кнопок для левого ограничения"""
        if checked:  # Выбрана «Имя левой точки»
            self.left_point_combo.setEnabled(True)
            self.left_padding_edit.setEnabled(False)
            self.left_padding_edit.setText("")
        else:  # Выбрана «Отступ влево»
            self.left_point_combo.setCurrentIndex(0)  # Устанавливаем «—»
            self.left_point_combo.setEnabled(False)
            self.left_padding_edit.setEnabled(True)

    def _on_right_radio_toggled(self, checked: bool):
        """Обработчик переключения радио-кнопок для правого ограничения"""
        if checked:  # Выбрана «Имя правой точки»
            self.right_point_combo.setEnabled(True)
            self.right_padding_edit.setEnabled(False)
            self.right_padding_edit.setText("")
        else:  # Выбрана «Отступ вправо»
            self.right_point_combo.setCurrentIndex(0)  # Устанавливаем «—»
            self.right_point_combo.setEnabled(False)
            self.right_padding_edit.setEnabled(True)


    def _create_form_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 1. Имя точки + выпадающий список
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Имя точки:"))

        self.point_combo = QComboBox()
        self.point_combo.addItem("—", None)  # Пустой вариант
        for point in self._points:
            self.point_combo.addItem(point.name, point)
        hlayout.addWidget(self.point_combo)
        layout.addLayout(hlayout)

        # 2. Комментарий
        layout.addWidget(QLabel("Комментарий:"))
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(60)
        layout.addWidget(self.comment_edit)

        # 3. Блок "Ограничение слева"
        left_group = QGroupBox("Ограничение слева")
        left_layout = QVBoxLayout(left_group)

        # Радио-кнопки
        self.left_point_radio = QRadioButton("Имя левой точки")
        self.left_padding_radio = QRadioButton("Отступ влево")
        left_layout.addWidget(self.left_point_radio)
        left_layout.addWidget(self.left_padding_radio)

        # Поле для имени точки (левое)
        hlayout_left_point = QHBoxLayout()
        hlayout_left_point.addWidget(QLabel("Точка:"))
        self.left_point_combo = QComboBox()
        self.left_point_combo.addItem("—", None)  # Пустой вариант
        for point in self._points:
            self.left_point_combo.addItem(point.name, point)
        hlayout_left_point.addWidget(self.left_point_combo)
        left_layout.addLayout(hlayout_left_point)

        # Поле для отступа (левое)
        hlayout_left_padding = QHBoxLayout()
        hlayout_left_padding.addWidget(QLabel("Отступ (t):"))
        self.left_padding_edit = QLineEdit()
        self.left_padding_edit.setPlaceholderText("0.0")
        hlayout_left_padding.addWidget(self.left_padding_edit)
        left_layout.addLayout(hlayout_left_padding)

        layout.addWidget(left_group)

        # 4. Блок "Ограничение справа"
        right_group = QGroupBox("Ограничение справа")
        right_layout = QVBoxLayout(right_group)

        # Радио-кнопки
        self.right_point_radio = QRadioButton("Имя правой точки")
        self.right_padding_radio = QRadioButton("Отступ вправо")
        right_layout.addWidget(self.right_point_radio)
        right_layout.addWidget(self.right_padding_radio)

        # Поле для имени точки (правое)
        hlayout_right_point = QHBoxLayout()
        hlayout_right_point.addWidget(QLabel("Точка:"))
        self.right_point_combo = QComboBox()
        self.right_point_combo.addItem("—", None)  # Пустой вариант (исправлено!)
        for point in self._points:
            self.right_point_combo.addItem(point.name, point)
        hlayout_right_point.addWidget(self.right_point_combo)
        right_layout.addLayout(hlayout_right_point)

        # Поле для отступа (правое)
        hlayout_right_padding = QHBoxLayout()
        hlayout_right_padding.addWidget(QLabel("Отступ (t):"))
        self.right_padding_edit = QLineEdit()
        self.right_padding_edit.setPlaceholderText("0.0")
        hlayout_right_padding.addWidget(self.right_padding_edit)
        right_layout.addLayout(hlayout_right_padding)

        layout.addWidget(right_group)

        return widget

    def _load_data_to_ui(self) -> None:
        # 1. Имя точки
        if self.original_data.target_point:
            index = self.point_combo.findData(self.original_data.target_point)
            if index != -1:
                self.point_combo.setCurrentIndex(index)
        else:
            self.point_combo.setCurrentIndex(0)  # Выбираем пустой вариант


        # 2. Комментарий
        self.comment_edit.setText(self.original_data.comment or "")


        # 3. Левое ограничение
        if self.original_data.left_point:
            self.left_point_radio.setChecked(True)
            index = self.left_point_combo.findData(self.original_data.left_point)
            if index != -1:
                self.left_point_combo.setCurrentIndex(index)
        elif self.original_data.left_padding_t is not None:
            self.left_padding_radio.setChecked(True)
            self.left_padding_edit.setText(str(self.original_data.left_padding_t))
        else:
            self.left_point_radio.setChecked(True)  # по умолчанию
            self.left_point_combo.setCurrentIndex(0)  # пустой вариант


        # 4. Правое ограничение
        if self.original_data.right_point:
            self.right_point_radio.setChecked(True)
            index = self.right_point_combo.findData(self.original_data.right_point)
            if index != -1:
                self.right_point_combo.setCurrentIndex(index)
        elif self.original_data.right_padding_t is not None:
            self.right_padding_radio.setChecked(True)
            self.right_padding_edit.setText(str(self.original_data.right_padding_t))
        else:
            self.right_point_radio.setChecked(True)  # по умолчанию
            self.right_point_combo.setCurrentIndex(0)  # пустой вариант

    def _collect_data_from_ui(self) -> Step:
        step_copy = deepcopy(self.original_data)


        # 1. Имя точки
        step_copy.target_point = self.point_combo.currentData()  # None, если выбран «—»

        # 2. Комментарий
        step_copy.comment = self.comment_edit.toPlainText()

        # 3. Левое ограничение
        if self.left_point_radio.isChecked():
            step_copy.left_point = self.left_point_combo.currentData()  # None, если «—»
            step_copy.left_padding_t = None
        elif self.left_padding_radio.isChecked():
            try:
                step_copy.left_padding_t = float(self.left_padding_edit.text())
            except ValueError:
                step_copy.left_padding_t = None
            step_copy.left_point = None

        # 4. Правое ограничение
        if self.right_point_radio.isChecked():
            step_copy.right_point = self.right_point_combo.currentData()  # None, если «—»
            step_copy.right_padding_t = None
        elif self.right_padding_radio.isChecked():
            try:
                step_copy.right_padding_t = float(self.right_padding_edit.text())
            except ValueError:
                step_copy.right_padding_t = None
            step_copy.right_point = None

        return step_copy




    def _validate_data(self) -> bool:
        has_target = self.point_combo.currentData() is not None
        return has_target


    def _emit_add_signal(self, form_data: Form) -> None:
        """Испускание сигнала добавления новой формы"""
        app_signals.db_add_form.emit(form_data)

    def _emit_update_signal(self, form_data: Form) -> None:
        """Испускание сигнала обновления формы"""
        app_signals.db_update_form_main_info.emit(form_data)


# Mock-тестирование
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QWidget

    # 1. Создаём mock-данные
    point_a = Point(id=1, name="Точка A")
    point_b = Point(id=2, name="Точка B")
    point_c = Point(id=3, name="Точка C")

    # Исходный шаг (будет редактироваться)
    original_step = Step(
        id=101,
        num_in_form=5,
        target_point=point_a,
        comment="Исходный комментарий",
        left_point=None,
        left_padding_t=0.5,
        right_point=point_b,
        right_padding_t=None,
        tracks=[]
    )

    # Список точек для выпадающих списков
    points = [point_a, point_b, point_c]

    # 2. Создаём экземпляр редактора
    # Инициализируем приложение
    app = QApplication(sys.argv)

    # Вариант 1: без родителя (модальное окно)
    editor = StepInfoEditor(parent=None, step=original_step, points=points)

    # Вариант 2: с родителем (если нужно встроить в другой виджет)
    # parent_widget = QWidget()
    # editor = StepInfoEditor(parent=parent_widget, step=original_step, points=points)
    # parent_widget.show()

    editor.show()
    sys.exit(app.exec())



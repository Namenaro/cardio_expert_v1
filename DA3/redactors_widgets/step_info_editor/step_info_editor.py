from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QRadioButton, QGroupBox
)
from DA3.redactors_widgets.base_editor import BaseEditor
from DA3 import app_signals
from CORE.db_dataclasses import *
from DA3.redactors_widgets.step_info_editor.limit_widget import LimitWidget

from copy import deepcopy


class StepInfoEditor(BaseEditor):
    """Редактор основной информации о шаге"""

    def __init__(self, parent: QWidget, step: Step, points: List[Point]):
        if not points:
            raise ValueError("Список точек не может быть пустым")

        self._points: List[Point] = points
        super().__init__(parent, step)
        self.setWindowTitle("Редактирование параметра")
        self.resize(400, 300)

    def _create_form_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # 1. Имя точки + выпадающий список
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Имя точки:"))
        self.point_combo = QComboBox()
        self._fill_combo_with_points(self.point_combo)
        hlayout.addWidget(self.point_combo)
        layout.addLayout(hlayout)


        # 2. Комментарий
        layout.addWidget(QLabel("Комментарий:"))
        self.comment_edit = QTextEdit()
        self.comment_edit.setMaximumHeight(60)
        layout.addWidget(self.comment_edit)

        # 3. Левое ограничение
        self.left_limit = LimitWidget(self, self._points, "Ограничение слева")
        layout.addWidget(self.left_limit)


        # 4. Правое ограничение
        self.right_limit = LimitWidget(self, self._points, "Ограничение справа")
        layout.addWidget(self.right_limit)

        return widget

    def _fill_combo_with_points(self, combo: QComboBox):
        """Заполняет QComboBox списком точек"""
        combo.addItem("—", None)
        for point in self._points:
            combo.addItem(point.name, point)

    def _load_data_to_ui(self) -> None:
        # 1. Имя точки
        if self.original_data.target_point:
            idx = self.point_combo.findData(self.original_data.target_point)
            if idx != -1:
                self.point_combo.setCurrentIndex(idx)
        else:
            self.point_combo.setCurrentIndex(0)

        # 2. Комментарий
        self.comment_edit.setText(self.original_data.comment or "")

        # 3. Левое ограничение
        self.left_limit.set_value(
            point=self.original_data.left_point,
            padding=self.original_data.left_padding_t
        )

        # 4. Правое ограничение
        self.right_limit.set_value(
            point=self.original_data.right_point,
            padding=self.original_data.right_padding_t
        )

    def _collect_data_from_ui(self) -> Step:
        step_copy = deepcopy(self.original_data)

        # 1. Имя точки
        step_copy.target_point = self.point_combo.currentData()

        # 2. Комментарий
        step_copy.comment = self.comment_edit.toPlainText()

        # 3. Левое ограничение
        left_point, left_padding = self.left_limit.get_value()
        step_copy.left_point = left_point
        step_copy.left_padding_t = left_padding

        # 4. Правое ограничение
        right_point, right_padding = self.right_limit.get_value()
        step_copy.right_point = right_point
        step_copy.right_padding_t = right_padding

        return step_copy

    def _validate_data(self) -> bool:
        return self.point_combo.currentData() is not None

    def _emit_add_signal(self, form_data: Form) -> None:
        app_signals.db_add_form.emit(form_data)

    def _emit_update_signal(self, form_data: Form) -> None:
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



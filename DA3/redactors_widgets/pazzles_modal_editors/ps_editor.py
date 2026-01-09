from typing import Optional, List
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout,
                               QGroupBox, QLineEdit, QLabel, QMessageBox)
from PySide6.QtCore import Qt

from CORE.db_dataclasses import BasePazzle, Form, BaseClass, Parameter, ClassArgument, ObjectArgumentValue, Track
from DA3 import app_signals
from DA3.app_signals import AddSMParams, Del_Upd_SM_PS_Params, AddPSParams
from DA3.redactors_widgets import BaseEditor
from DA3.redactors_widgets.pazzles_subwidgets  import (ArgumentsTableWidget, ClassesListWidget, InputParamsWidget)


class PSEditor(BaseEditor):
    """Редактор для SM объектов """

    def __init__(self, parent: QWidget,
                 ps: BasePazzle,
                 classes_refs: List[BaseClass],
                 track: Optional[Track],
                 step_id:int
                 ):
        self._classes_refs = classes_refs
        self.track = track
        self.step_id = step_id


        super().__init__(parent, ps)
        self.setWindowTitle("Редактор SM объекта (signal modification)")
        self.resize(600, 700)

    def _create_form_widget(self) -> QWidget:
        """Создание виджета с полями ввода"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Основные поля объекта
        group_box = QGroupBox("Параметры PS объекта")
        group_layout = QFormLayout(group_box)
        group_layout.setContentsMargins(15, 15, 15, 15)
        group_layout.setSpacing(10)
        group_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.id_label = QLabel(str(self.original_data.id) if self.original_data else "Новый")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите имя PS объекта")
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("Введите комментарий")

        group_layout.addRow("ID:", self.id_label)
        group_layout.addRow("Имя:", self.name_edit)
        group_layout.addRow("Комментарий:", self.comment_edit)

        layout.addWidget(group_box)

        # Выбор класса
        class_group = QGroupBox("Выбор класса")
        class_layout = QVBoxLayout(class_group)
        class_layout.setContentsMargins(15, 15, 15, 15)

        self.classes_widget = ClassesListWidget(self._classes_refs)
        self.classes_widget.class_selected.connect(self._on_class_selected)
        class_layout.addWidget(self.classes_widget)
        layout.addWidget(class_group)

        # Простой заголовок
        hc_title = QLabel(" Селектор особых точек на сигнале")
        hc_title.setStyleSheet("font-weight: bold; font-size: 13px; padding: 5px;")
        layout.addWidget(hc_title)

        # Аргументы конструктора
        self.arguments_widget = ArgumentsTableWidget()
        layout.addWidget(self.arguments_widget)

        layout.addStretch()

        return widget

    def _on_class_selected(self, selected_class: BaseClass):
        """Обработчик выбора класса"""
        # Загружаем аргументы конструктора
        self.arguments_widget.load_arguments(selected_class.constructor_arguments)


    def _load_data_to_ui(self) -> None:
        """Загрузка данных из объекта в интерфейс"""
        # Основные поля
        if self.original_data:
            self.name_edit.setText(self.original_data.name)
        if self.original_data:
            self.comment_edit.setText(self.original_data.comment)

        self._load_class_ref()

        # Загружаем сохраненные значения аргументов
        if self.original_data:
            self.arguments_widget.load_current_values(self.original_data.argument_values)


    def _load_class_ref(self):
        if self.original_data:

            self.classes_widget.set_selected_class(self.original_data.class_ref)
            self.arguments_widget.load_arguments(self.original_data.class_ref.constructor_arguments)


    def _collect_data_from_ui(self) -> BasePazzle:
        """Сбор данных из интерфейса в объект"""
        updated_ps = BasePazzle()

        # Получаем основные поля
        updated_ps.id = self.original_data.id if self.original_data else None
        updated_ps.name = self.name_edit.text().strip() or None
        updated_ps.comment = self.comment_edit.text().strip()

        # Получаем сигнатуру класса
        updated_ps.class_ref = self.classes_widget.get_selected_class()

        # Получаем значения для аругметов конструктора
        updated_ps.argument_values = self.arguments_widget.get_argument_values()

        return updated_ps

    def _validate_data(self) -> bool:
        """Проверка корректности данных"""
        # Проверяем, что выбран класс
        if not self.classes_widget.get_selected_class():
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите класс ")
            return False

        return True

    def _emit_add_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала добавления нового объекта. """

        # Тут два варианта:
        # 1) пазл добавляется в существующий трек
        # 2) трек создается новый и в него кладется этот пазл

        if self.track is None:
            add_ps_params = AddPSParams(ps=data,
                                        track_id=None,
                                        step_id=self.step_id)
        else:
            add_ps_params = AddPSParams(ps=data,
                                        track_id=self.track.id,
                                        step_id=self.step_id)
        app_signals.base_pazzle.db_add_ps.emit(add_ps_params)

    def _emit_update_signal(self, data: BasePazzle) -> None:
        """Испускание сигнала обновления существующего объекта"""
        upd_params = Del_Upd_SM_PS_Params(pazzle=data, track_id=self.track.id)
        app_signals.base_pazzle.db_update_ps_sm.emit(upd_params)

# тестирование
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    # Создаём тестовые объекты
    test_class = BaseClass(
        id=1,
        name="TestClass",
        comment="Тестовый класс для проверки редактора",
        type="PS",
        constructor_arguments=[
            ClassArgument(name="arg1", default_value="dfdf", class_id=2, comment="ddfdf"),
            ClassArgument(name="arg2", default_value="fdfdf", class_id=1, comment="dfdf"),
        ]
    )

    test_pazzle = BasePazzle(
        id=None,
        name="Тестовый PS объект",
        comment="Это тестовый объект для PSEditor",
        class_ref=test_class,
        argument_values=[
            ObjectArgumentValue(argument_value="dfdf", argument_id=1, id=1),
            ObjectArgumentValue(argument_value="dfdf", argument_id=1, id=1),
        ]
    )
    classes_refs = [test_class]

    #  Создаём экземпляр редактора
    editor = PSEditor(
        parent=None,
        ps=test_pazzle,
        classes_refs=classes_refs,
        step_id=9,
        track=None
    )
    editor.show()
    sys.exit(app.exec())

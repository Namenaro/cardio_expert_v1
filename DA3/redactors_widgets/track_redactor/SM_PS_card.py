
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                              QWidget, QFrame, QLabel, QSizePolicy, QMenu)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPalette, QColor
from typing import List, Optional

from CORE.db_dataclasses import BaseClass, BasePazzle
from DA3 import app_signals
from DA3.app_signals import AddSMParams, AddPSParams, Del_Upd_SM_PS_Params


class SM_PS_Card(QFrame):
    def __init__(self, puzzle: BasePazzle, refs: List[BaseClass],
                 track_id: Optional[int], step_id: int,
                 num_in_track: int,
                 parent=None):
        super().__init__(parent)

        # Сохраняем все аргументы как поля класса
        self.puzzle = puzzle
        self.SMs_refs = refs
        self.track_id = track_id
        self.step_id = step_id
        self.num_in_track = num_in_track

        # Инициализируем UI
        self.setup_ui()

        # Устанавливаем фильтр событий для обработки кликов
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Обработчик событий для фильтрации кликов по карточке."""
        if obj is self and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self._on_left_click(event)
            elif event.button() == Qt.RightButton:
                self._on_right_click(event)
        return super().eventFilter(obj, event)

    def _on_left_click(self, event):
        """Обработка левого клика — эмитируем соответствующий сигнал."""
        if self.is_SM():
            params = AddSMParams(
                sm=self.puzzle,
                track_id=self.track_id,
                num_in_track=self.num_in_track,
                step_id=self.step_id
            )
            app_signals.base_pazzle.request_sm_redactor.emit(params)
        elif self.is_PS():
            params = AddPSParams(
                ps=self.puzzle,
                track_id=self.track_id,
                step_id=self.step_id
            )
            app_signals.base_pazzle.request_ps_redactor.emit(params)

    def _on_right_click(self, event):
        """Обработка правого клика — показываем контекстное меню."""
        menu = QMenu(self)

        # Действия для добавления SM
        add_sm_left = menu.addAction("Добавить SM слева")
        add_sm_right = menu.addAction("Добавить SM справа")

        # Действия для добавления PS
        add_ps = menu.addAction("Добавить PS")


        # Действие для удаления
        delete_action = menu.addAction("Удалить карту")

        # Подключаем обработчики
        add_sm_left.triggered.connect(self._add_sm_left)
        add_sm_right.triggered.connect(self._add_sm_right)
        add_ps.triggered.connect(self._add_ps)
        delete_action.triggered.connect(self._delete_card)

        # Показываем меню в позиции курсора
        menu.exec(event.globalPos())

    def _add_sm_left(self):
        """Эмитируем сигнал для добавления SM слева."""
        params = AddSMParams(
            sm=None,
            track_id=self.track_id,
            num_in_track=self.num_in_track - 1,
            step_id=self.step_id
        )
        app_signals.base_pazzle.request_sm_redactor.emit(params)

    def _add_sm_right(self):
        """Эмитируем сигнал для добавления SM справа."""
        params = AddSMParams(
            sm=None,
            track_id=self.track_id,
            num_in_track=self.num_in_track + 1,
            step_id=self.step_id
        )
        app_signals.base_pazzle.request_sm_redactor.emit(params)

    def _add_ps(self):
        """Эмитируем сигнал для добавления PS слева."""
        params = AddPSParams(
            ps=None,
            track_id=self.track_id,
            step_id=self.step_id
        )
        app_signals.base_pazzle.request_ps_redactor.emit(params)


    def _delete_card(self):
        """Эмитируем сигнал для удаления карты."""
        del_params = Del_Upd_SM_PS_Params(pazzle=self.puzzle, track_id=self.track_id)
        app_signals.base_pazzle.db_delete_ps_sm.emit(del_params)

    def setup_ui(self):
        """Инициализация пользовательского интерфейса карточки."""
        # Настройка внешнего вида карточки
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)

        # Фон определяется типом паззла
        palette = self.palette()
        if self.is_PS():
            color = QColor(0, 255, 76)
        else:
            color = QColor(255, 255, 200)  # Светло‑жёлтый
        palette.setColor(QPalette.Window, color)

        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Создаём вертикальный макет
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)  # Отступы по краям
        layout.setSpacing(8)  # Расстояние между элементами

        # Поле ID (используем step_id)
        self.id_label = QLabel(f"ID: {self.puzzle.id}")
        self.id_label.setAlignment(Qt.AlignLeft)
        self.id_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Поле Comment (из puzzle.comment)
        self.comment_label = QLabel(f"Comment: {self.puzzle.comment}")
        self.comment_label.setAlignment(Qt.AlignLeft)
        self.comment_label.setWordWrap(True)  # Перенос строк при необходимости

        # Поле Class Ref Name (берём name из каждого элемента SMs_refs)
        if self.puzzle.class_ref:
            class_name = self.puzzle.class_ref.name
        else:
            class_name = "N/A"
        self.class_ref_label = QLabel(f"Class Ref: {class_name}")
        self.class_ref_label.setAlignment(Qt.AlignLeft)

        # Добавляем элементы в макет
        layout.addWidget(self.id_label)
        layout.addWidget(self.comment_label)
        layout.addWidget(self.class_ref_label)

        self.setLayout(layout)

        # Фиксируем минимальный размер
        self.setMinimumSize(200, 150)
        # Размерная политика — может расширяться по горизонтали и вертикали
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def is_SM(self):
        return self.puzzle.is_SM()

    def is_PS(self):
        return self.puzzle.is_PS()


if __name__ == "__main__":
    # Mock-заглушки для используемых классов

    class BasePazzle:
        def __init__(self):
            self.id = 1
            self.comment = "Пример комментария к паззлу"
            # Ссылка на класс
            self.class_ref: Optional[BaseClass] = None
            self.is_ps: bool = False

        def is_PS(self):
            return self.is_ps

        def is_SM(self):
            return not self.is_ps


    class BaseClass:
        def __init__(self, name: str):
            self.name = name


    app = QApplication([])

    window = QMainWindow()
    window.setWindowTitle("Тест SMCard")
    window.resize(400, 300)

    # Создаём центральный виджет
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Вертикальный макет для главного окна
    main_layout = QVBoxLayout(central_widget)
    main_layout.setAlignment(Qt.AlignTop)

    # Создаём тестовые данные
    puzzle = BasePazzle()
    # Привязываем class_ref к puzzle (как в заглушке)
    puzzle.class_ref = BaseClass("PuzzleClass")

    refs = [
        BaseClass("ClassA"),
        BaseClass("ClassB"),
        BaseClass("ClassC")
    ]
    track_id = 42
    step_id = 101

    # Создаём экземпляр карточки
    card = SM_PS_Card(puzzle, refs, track_id, step_id, num_in_track=0)

    # Добавляем карточку в макет
    main_layout.addWidget(card)

    window.show()
    app.exec()



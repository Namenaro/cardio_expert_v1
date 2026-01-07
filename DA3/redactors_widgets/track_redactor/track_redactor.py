from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout,
                              QVBoxLayout, QWidget, QFrame, QLabel, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from typing import List, Optional
from dataclasses import field

from CORE.db_dataclasses import Track, BasePazzle, BaseClass
from DA3.redactors_widgets.track_redactor.SM_PS_card import SM_PS_Card




class TrackRedactor(QFrame):
    def __init__(self, track: Track, step_id: int,
                 PSs_refs: List[BaseClass], SMs_refs: List[BaseClass],
                 parent=None):
        super().__init__(parent)

        # Сохраняем аргументы как поля класса
        self.track = track
        self.step_id = step_id
        self.PSs_refs = PSs_refs
        self.SMs_refs = SMs_refs

        # Инициализируем UI
        self.setup_ui()

    def setup_ui(self):
        """Инициализация пользовательского интерфейса карточки трека."""
        # Настройка внешнего вида карточки
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setLineWidth(2)

        # Светло‑серый фон для карточки трека
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Основной вертикальный макет
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # Заголовок с ID трека
        self.id_label = QLabel(f"Track ID: {self.track.id or 'N/A'}")
        self.id_label.setAlignment(Qt.AlignCenter)
        self.id_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #444;")
        main_layout.addWidget(self.id_label)

        # Горизонтальный макет для карточек SM и PS
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(10)

        # Добавляем карточки SM (в порядке из списка SMs)
        for idx, puzzle in enumerate(self.track.SMs):
            card = SM_PS_Card(
                puzzle=puzzle,
                refs=self.SMs_refs,
                track_id=self.track.id,
                step_id=self.step_id,
                num_in_track=idx  # ← Правильный индекс (int)
            )
            cards_layout.addWidget(card)

        # Добавляем карточки PS
        for puzzle in self.track.PSs:
            card = SM_PS_Card(
                puzzle=puzzle,
                refs=self.PSs_refs,
                track_id=self.track.id,
                step_id=self.step_id,
                num_in_track=-1
            )
            cards_layout.addWidget(card)

        main_layout.addLayout(cards_layout)
        self.setLayout(main_layout)

        # Фиксируем минимальный размер
        self.setMinimumSize(300, 200)
        # Размерная политика — может расширяться по горизонтали и вертикали
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def refresh(self, track: Track):
        """Обновляет данные трека и полностью пересоздаёт UI."""
        self.track = track

        # Полностью очищаем текущий layout
        if self.layout():
            # Удаляем все дочерние виджеты
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Пересоздаём UI с новыми данными
        self.setup_ui()

        # Обновляем геометрию
        self.updateGeometry()

# Мок-тест
if __name__ == "__main__":
    import sys
    from dataclasses import dataclass


    # Mock-заглушки для используемых классов (для теста)
    class BasePazzle:
        def __init__(self, is_ps: bool = False, comment: str = "Пример комментария"):
            self.id = 1
            self.comment = comment
            self.class_ref: Optional[BaseClass] = None
            self.is_ps = is_ps

        def is_PS(self):
            return self.is_ps

        def is_SM(self):
            return not self.is_ps


    class BaseClass:
        def __init__(self, name: str):
            self.name = name


    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Тест TrackCard")
    window.resize(800, 400)

    # Создаём центральный виджет
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Вертикальный макет для главного окна
    main_layout = QVBoxLayout(central_widget)
    main_layout.setAlignment(Qt.AlignTop)
    main_layout.setSpacing(15)

    # Создаём тестовые данные
    # SM паззлы
    sm1 = BasePazzle(is_ps=False, comment="SM комментарий 1")
    sm2 = BasePazzle(is_ps=False, comment="SM комментарий 2")

    # PS паззлы
    ps1 = BasePazzle(is_ps=True, comment="PS комментарий 1")
    ps2 = BasePazzle(is_ps=True, comment="PS комментарий 2")

    # Ссылки на классы
    sm_refs = [BaseClass("SMClassA"), BaseClass("SMClassB")]
    ps_refs = [BaseClass("PSClassX"), BaseClass("PSClassY")]

    # Создаём трек
    track = Track(
        id=1001,
        SMs=[sm1, sm2],
        PSs=[ps1, ps2]
    )

    step_id = 202


    track_card = TrackRedactor(track, step_id, ps_refs, sm_refs)

    # Добавляем карточку в макет
    main_layout.addWidget(track_card)

    window.show()
    sys.exit(app.exec())


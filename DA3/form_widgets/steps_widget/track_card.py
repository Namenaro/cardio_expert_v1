from CORE.db_dataclasses import *
from dataclasses import dataclass, field
from typing import Optional, List
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QFormLayout, QLabel, QPushButton, QApplication, QHBoxLayout
)
from PySide6.QtCore import Qt


class TrackCard(QFrame):
    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        self.track = track
        self.setup_ui()

    def setup_ui(self):
        # Основной макет
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Форма для отображения данных
        form_layout = QFormLayout()
        layout.addLayout(form_layout)

        # ID
        self.id_label = QLabel()
        if self.track.id is not None:
            self.id_label.setNum(self.track.id)
        form_layout.addRow("ID:", self.id_label)

        # Длина списка SMs
        self.sms_count_label = QLabel()
        self.sms_count_label.setNum(len(self.track.SMs))
        form_layout.addRow("Количество SM:", self.sms_count_label)

        # Длина списка PSs
        self.pss_count_label = QLabel()
        self.pss_count_label.setNum(len(self.track.PSs))
        form_layout.addRow("Количество PS:", self.pss_count_label)

        # Горизонтальный макет для кнопок
        buttons_layout = QHBoxLayout()

        # Кнопка "редактировать"
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.on_edit_clicked)
        buttons_layout.addWidget(self.edit_button)

        # Кнопка "удалить трек"
        self.delete_button = QPushButton("Удалить трек")
        self.delete_button.clicked.connect(self.on_delete_clicked)
        buttons_layout.addWidget(self.delete_button)

        layout.addLayout(buttons_layout)

    def on_edit_clicked(self):
        # Заглушка для обработчика нажатия "редактировать"
        print(f"Кнопка 'Редактировать' нажата для трека ID={self.track.id}. Реализация пока отсутствует.")

    def on_delete_clicked(self):
        # Заглушка для обработчика нажатия "удалить трек"
        print(f"Кнопка 'Удалить трек' нажата для трека ID={self.track.id}. Реализация пока отсутствует.")


# Mock-тестирование
if __name__ == "__main__":
    import sys

    # Создаем mock-данные для тестирования
    pazzle1 = BasePazzle()
    pazzle2 = BasePazzle()
    pazzle3 = BasePazzle()
    pazzle4 = BasePazzle()

    track = Track(
        id=201,
        SMs=[pazzle1, pazzle2, pazzle3],  # 3 элемента
        PSs=[pazzle4]  # 1 элемент
    )

    # Инициализируем приложение
    app = QApplication(sys.argv)

    # Создаем и показываем виджет
    widget = TrackCard(track)
    widget.setWindowTitle("TrackCard Test")
    widget.resize(300, 200)
    widget.show()

    sys.exit(app.exec())
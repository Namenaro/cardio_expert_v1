from CORE.db_dataclasses import *
from dataclasses import dataclass, field
from typing import Optional, List
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QFormLayout, QLabel, QApplication, QWidget
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QMouseEvent


class TrackCard(QFrame):
    # Начальный стиль виджета
    _DEFAULT_STYLE = """
            TrackCard {
                background-color: #f0f0f0;
                border-radius: 4px;
                border: 1px solid #dcdcdc;
            }
        """
    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        self.track = track
        self.setMouseTracking(True)  # Включаем отслеживание мыши
        self._is_hovered = False  # Флаг наведения курсора

        # Устанавливаем начальный стиль
        self.setStyleSheet(self._DEFAULT_STYLE)

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

    # Обработчик события наведения курсора
    def enterEvent(self, event: QEvent):
        self._is_hovered = True
        self._update_style()
        super().enterEvent(event)

    # Обработчик события ухода курсора
    def leaveEvent(self, event: QEvent):
        self._is_hovered = False
        self._update_style()
        super().leaveEvent(event)

    # Обработчик клика по виджету
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click()
        super().mousePressEvent(event)

    # Метод-заглушка для обработки клика
    def on_click(self):
        print(f"Виджет TrackCard кликнут. ID трека: {self.track.id}")

    def _update_style(self):
        if self._is_hovered:
            self.setStyleSheet("""
                TrackCard {
                    background-color: #e0e0e0;
                    border-radius: 4px;
                    border: 1px solid #b0b0b0;
                }
            """)
        else:
            # Используем сохранённый начальный стиль
            self.setStyleSheet(self._DEFAULT_STYLE)


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

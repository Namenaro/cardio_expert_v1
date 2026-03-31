"""
Виджет для навигации по датасету с кнопками "Вперед" и "Назад"
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy
)

from DA3.simulation_app.simulator_signals import get_signals


class DatasetNavigator(QWidget):
    """
    Виджет для навигации по датасету.

    Содержит кнопки "Назад" и "Вперед" и поле для отображения ID текущего примера.
    При нажатии на кнопки эмитирует сигналы requested_prev и requested_next.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Получаем глобальные сигналы
        self.signals = get_signals()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Настройка пользовательского интерфейса"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Кнопка "Назад"
        self.prev_button = QPushButton("← Назад")
        self.prev_button.setMinimumWidth(80)
        self.prev_button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

        # Поле с ID примера (нередактируемое) - компактное
        self.id_label = QLabel("—")
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.id_label.setMinimumWidth(120)
        self.id_label.setMaximumHeight(28)  # Ограничиваем высоту
        self.id_label.setFrameStyle(QLabel.Shape.Panel | QLabel.Shadow.Sunken)
        self.id_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                color: #333333;
                padding: 4px 8px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-family: monospace;
                font-size: 11pt;
            }
        """)

        # Кнопка "Вперед"
        self.next_button = QPushButton("Вперед →")
        self.next_button.setMinimumWidth(80)
        self.next_button.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed
        )

        # Добавляем виджеты в layout
        layout.addStretch()  # Растягивающийся пробел слева
        layout.addWidget(self.prev_button)
        layout.addWidget(self.id_label)
        layout.addWidget(self.next_button)
        layout.addStretch()  # Растягивающийся пробел справа

        # Устанавливаем стили для кнопок (светлая тема)
        self._setup_button_styles()

    def _setup_button_styles(self):
        """Настройка стилей кнопок (светлая тема)"""
        button_style = """
            QPushButton {
                background-color: #e0e0e0;
                color: #333333;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 5px 12px;
                font-size: 11pt;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                border-color: #a0a0a0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #a0a0a0;
                border-color: #d0d0d0;
            }
        """
        self.prev_button.setStyleSheet(button_style)
        self.next_button.setStyleSheet(button_style)

    def _connect_signals(self):
        """Подключение сигналов кнопок к глобальным сигналам"""
        self.prev_button.clicked.connect(self._on_prev_clicked)
        self.next_button.clicked.connect(self._on_next_clicked)

    def _on_prev_clicked(self):
        """Обработка нажатия кнопки "Назад" """
        self.signals.requested_prev.emit()

    def _on_next_clicked(self):
        """Обработка нажатия кнопки "Вперед" """
        self.signals.requested_next.emit()

    def set_example_id(self, example_id: str) -> None:
        """
        Устанавливает текст в поле с ID примера.

        Args:
            example_id: ID примера для отображения
        """
        self.id_label.setText(str(example_id))

    def get_example_id(self) -> str:
        """
        Возвращает текущий отображаемый ID примера.

        Returns:
            Текущий ID примера или строку "—", если ID не установлен
        """
        return self.id_label.text()

    def set_buttons_enabled(self, prev_enabled: bool, next_enabled: bool) -> None:
        """
        Устанавливает доступность кнопок навигации.

        Args:
            prev_enabled: доступна ли кнопка "Назад"
            next_enabled: доступна ли кнопка "Вперед"
        """
        self.prev_button.setEnabled(prev_enabled)
        self.next_button.setEnabled(next_enabled)

    def clear(self) -> None:
        """
        Очищает поле с ID примера и блокирует кнопки.
        """
        self.id_label.setText("—")
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)


# Пример использования виджета (для тестирования)
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow


    class TWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Тест DatasetNavigator")
            self.setCentralWidget(DatasetNavigator())
            self.resize(400, 100)

            # Получаем сигналы и подключаем их
            signals = get_signals()
            signals.requested_prev.connect(self.on_prev)
            signals.requested_next.connect(self.on_next)

        def on_prev(self):
            print("Запрошен предыдущий пример")

        def on_next(self):
            print("Запрошен следующий пример")


    app = QApplication(sys.argv)
    window = TWindow()
    window.show()
    sys.exit(app.exec())

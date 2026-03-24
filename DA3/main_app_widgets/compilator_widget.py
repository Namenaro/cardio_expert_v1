from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor


class CompilerWindow(QDialog):
    """
    Модальное окно для отображения результата компиляции.
    """

    def __init__(self, success: bool, report: str, parent=None):
        """

        :param success: флаг успеха компиляции
        :param report: текст отчёта о компиляции
        :param parent: родительское окно
        """
        super().__init__(parent)

        self.success = success
        self.report = report

        # Делаем окно модальным
        self.setModal(True)
        self.setWindowTitle("Результат компиляции")
        self.setMinimumSize(600, 400)

        self.setup_ui()
        self.apply_style()

    def setup_ui(self):
        """Настройка интерфейса окна"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок с результатом
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(self.result_label)

        # Текстовое поле для отчёта (нередактируемое)
        self.report_text = QTextEdit()
        self.report_text.setPlainText(self.report)
        self.report_text.setReadOnly(True)
        self.report_text.setStyleSheet(
            "background-color: #f9f9f9; border: 1px solid #cccccc; padding: 5px;"
        )
        layout.addWidget(self.report_text)

        # Кнопка закрытия
        self.close_button = QPushButton("Закрыть")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setMinimumHeight(35)
        layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignRight)

    def apply_style(self):
        """Применяет стиль в зависимости от результата компиляции"""
        if self.success:
            # Успешная компиляция — зелёный фон
            self.result_label.setText("✓ УСПЕШНО")
            background_color = QColor("#d4edda")  # Светло-зелёный
            text_color = QColor("#155724")  # Тёмно-зелёный текст
        else:
            # Ошибка компиляции — красный фон
            self.result_label.setText("✗ ЕСТЬ ОШИБКИ")
            background_color = QColor("#f8d7da")  # Светло-красный
            text_color = QColor("#721c24")  # Тёмно-красный текст

        # Устанавливаем цвета для всего окна
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, background_color)
        palette.setColor(QPalette.ColorRole.WindowText, text_color)
        self.setPalette(palette)

        # Обновляем стиль для всех виджетов
        self.setAutoFillBackground(True)
        self.update()

    def showEvent(self, event):
        """
        Переопределённый метод для дополнительной настройки при показе окна.
        Обеспечивает корректное применение стилей.
        """
        super().showEvent(event)
        # Принудительно обновляем стиль при показе
        self.apply_style()


if __name__ == "__main__":
    # Пример успешного выполнения
    compiler_window = CompilerWindow(success=True, report="Компиляция завершена успешно!\nВсе модули собраны.")
    compiler_window.exec()

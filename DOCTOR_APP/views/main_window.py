import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget,
                               QVBoxLayout, QHBoxLayout, QFrame, QLabel)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DoctorApp")
        self.setGeometry(100, 100, 1000, 700) # позиция экрана
 
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной вертикальный layout (верх/низ)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # верхняя область (3 контейнера)
        top_area = self.create_top_area()
        main_layout.addWidget(top_area, 1)  # 50% высоты

        # нижняя область (3 контейнера)
        bottom_area = self.create_bottom_area()
        main_layout.addWidget(bottom_area, 1)  # 50% высоты

    def create_top_area(self):
        """Создает верхнюю область"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1"]

        container1 = self.create_container(colors[0])
        layout.addWidget(container1, 2)

        container2 = self.create_container(colors[1])
        layout.addWidget(container2, 1)

        container3 = self.create_container(colors[2])
        layout.addWidget(container3, 3)

        return widget

    def create_bottom_area(self):
        """Создает нижнюю область"""
        widget = QWidget()
        main_bottom_layout = QHBoxLayout(widget)
        main_bottom_layout.setSpacing(5)
        main_bottom_layout.setContentsMargins(0, 0, 0, 0)

        left_split_area = self.create_left_split_area()
        main_bottom_layout.addWidget(left_split_area, 2)

        right_area = self.create_container("#FFEAA7")
        main_bottom_layout.addWidget(right_area, 1)

        return widget

    def create_left_split_area(self):
        """Создает левую часть нижней области, разделенную на 2 вертикально"""
        widget = QWidget()
        # Вертикальная компоновка для левой части
        left_layout = QVBoxLayout(widget)
        left_layout.setSpacing(5)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя половина левой части
        top_left = self.create_container("#96CEB4")
        left_layout.addWidget(top_left)

        # Нижняя половина левой части
        bottom_left = self.create_container("#C8E6C9")
        left_layout.addWidget(bottom_left)

        return widget

    def create_container(self, color):
        """Создает обычный контейнер с заголовком"""
        container = QFrame()
        container.setFrameStyle(QFrame.Box)
        container.setLineWidth(2)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: 2px solid #333;
                border-radius: 5px;
            }}
        """)

        return container


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
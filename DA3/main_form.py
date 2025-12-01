from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QSizePolicy)
from DA3.form_widgets import (
    FormInfoWidget, HCsWidget, PCsWidget,
    PointsWidget, ParametersWidget, StepsWidget
)


class MainForm(QMainWindow):
    """Главная форма приложения"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Главная форма приложения")
        self.resize(800, 600)

        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Главный вертикальный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # === ВЕРХНИЙ КОНТЕЙНЕР (65% высоты) ===
        top_container = QWidget()
        top_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        top_layout = QHBoxLayout(top_container)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # FormInfoWidget (30% ширины)
        form_info_widget = FormInfoWidget()
        top_layout.addWidget(form_info_widget, 30)

        # PointsWidget (20% ширины)
        points_widget = PointsWidget()
        top_layout.addWidget(points_widget, 20)

        # StepsWidget (50% ширины)
        steps_widget = StepsWidget()
        top_layout.addWidget(steps_widget, 50)

        # === НИЖНИЙ КОНТЕЙНЕР (35% высоты) ===
        bottom_container = QWidget()
        bottom_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setSpacing(5)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Левый виджет - ParametersWidget
        parameters_widget = ParametersWidget()
        bottom_layout.addWidget(parameters_widget, 50)

        # Правый контейнер (для PC и HC виджетов)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # PCsWidget (сверху)
        pcs_widget = PCsWidget()
        right_layout.addWidget(pcs_widget, 50)

        # HCsWidget (снизу)
        hcs_widget = HCsWidget()
        right_layout.addWidget(hcs_widget, 50)

        bottom_layout.addWidget(right_container, 50)

        # Добавляем контейнеры в главный layout с пропорциями
        main_layout.addWidget(top_container, 65)  # 65% высоты
        main_layout.addWidget(bottom_container, 35)  # 35% высоты
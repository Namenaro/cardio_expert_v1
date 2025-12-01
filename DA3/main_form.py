from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QSizePolicy)
from CORE.db_dataclasses import Form
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
        self.form_info_widget = FormInfoWidget()
        top_layout.addWidget(self.form_info_widget, 30)

        # PointsWidget (20% ширины)
        self.points_widget = PointsWidget()
        top_layout.addWidget(self.points_widget, 20)

        # StepsWidget (50% ширины)
        self.steps_widget = StepsWidget()
        top_layout.addWidget(self.steps_widget, 50)

        # === НИЖНИЙ КОНТЕЙНЕР (35% высоты) ===
        bottom_container = QWidget()
        bottom_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setSpacing(5)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # ParametersWidget (50% ширины)
        self.parameters_widget = ParametersWidget()
        bottom_layout.addWidget(self.parameters_widget, 50)

        # Правый контейнер (для PC и HC виджетов)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # PCsWidget (сверху)
        self.pcs_widget = PCsWidget()
        right_layout.addWidget(self.pcs_widget, 50)

        # HCsWidget (снизу)
        self.hcs_widget = HCsWidget()
        right_layout.addWidget(self.hcs_widget, 50)

        bottom_layout.addWidget(right_container, 50)

        # Добавляем контейнеры в главный layout с пропорциями
        main_layout.addWidget(top_container, 65)  # 65% высоты
        main_layout.addWidget(bottom_container, 35)  # 35% высоты

    def refresh(self, form: Form) -> None:
        """
        Обновить все виджеты главной формы на основе переданной формы

        Args:
            form: Объект Form для отображения
        """
        # Обновляем виджет основной информации
        self.form_info_widget.reset_form(form)

        # Здесь в будущем можно будет добавить обновление других виджетов:
        # self.points_widget.refresh(form.points)
        # self.parameters_widget.refresh(form.parameters)
        # self.steps_widget.refresh(form.steps)
        # self.pcs_widget.refresh(form.HC_PC_objects)
        # self.hcs_widget.refresh(form.HC_PC_objects)

        # На данный момент другие виджеты просто показывают кнопку "Запустить редактор"
        # и не зависят от конкретной формы


# Пример использования:
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from CORE.db_dataclasses import Form

    app = QApplication(sys.argv)

    # Создаем тестовую форму
    test_form = Form(
        id=1,
        name="Тестовая форма",
        comment="Это тестовая форма для демонстрации",
        path_to_pic="",
        path_to_dataset="",
        points=[],
        parameters=[],
        steps=[],
        HC_PC_objects=[]
    )

    window = MainForm()

    # Пример вызова refresh с тестовой формой
    window.refresh(test_form)

    window.show()
    sys.exit(app.exec())
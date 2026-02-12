from PySide6.QtCore import Slot
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QScrollArea, QApplication)

from CORE.db_dataclasses import Form
from DA3 import app_signals
from DA3.form_widgets import (FormInfoWidget, HCsWidget, PCsWidget, PointsWidget, ParametersWidget, StepsWidget)


class MainForm(QMainWindow):
    """Главная форма приложения"""

    def __init__(self):
        super().__init__()

        # Устанавливаем адаптивный размер (% от экрана)
        screen = QApplication.primaryScreen().size()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        self.resize(width, height)

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Главная форма приложения")

        # Добавляем меню
        self.setup_menu()

        # Создаем центральный виджет с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Основной контейнер
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)

        # Главный вертикальный layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # === ВЕРХНИЙ КОНТЕЙНЕР ===
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # FormInfoWidget - минимальный размер по содержимому
        self.form_info_widget = FormInfoWidget()
        self.form_info_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        top_layout.addWidget(self.form_info_widget)

        # PointsWidget - расширяемый по горизонтали
        self.points_widget = PointsWidget()
        self.points_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        top_layout.addWidget(self.points_widget, stretch=1)

        # StepsWidget - максимальный приоритет расширения
        self.steps_widget = StepsWidget()
        self.steps_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        top_layout.addWidget(self.steps_widget, stretch=2)

        # === НИЖНИЙ КОНТЕЙНЕР ===
        bottom_container = QWidget()
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setSpacing(5)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # ParametersWidget
        self.parameters_widget = ParametersWidget()
        self.parameters_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bottom_layout.addWidget(self.parameters_widget, 1)

        # Правый контейнер (для PC и HC виджетов)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setSpacing(5)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # PCsWidget
        self.pcs_widget = PCsWidget()
        self.pcs_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        right_layout.addWidget(self.pcs_widget)

        # HCsWidget
        self.hcs_widget = HCsWidget()
        self.hcs_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        right_layout.addWidget(self.hcs_widget)

        bottom_layout.addWidget(right_container, 2)

        # Добавляем контейнеры в главный layout
        main_layout.addWidget(top_container)
        main_layout.addWidget(bottom_container)

        # Устанавливаем stretch factors
        main_layout.setStretch(0, 1)  # top_container
        main_layout.setStretch(1, 1)  # bottom_container

    def refresh(self, form: Form) -> None:
        """
        Обновить все виджеты главной формы на основе переданной формы

        Args:
            form: Объект Form для отображения
        """
        # Обновляем виджет основной информации
        self.form_info_widget.reset_form(form)
        self.points_widget.reset_points(form.points)
        self.parameters_widget.reset_parameters(form.parameters)
        self.hcs_widget.reset_form(form)
        self.pcs_widget.reset_form(form)
        self.steps_widget.reset_steps(form.steps)

    def setup_menu(self):
        """Создать и настроить главное меню приложения"""
        menu_bar = self.menuBar()

        # Меню «Компилировать»
        compile_menu = menu_bar.addMenu("Компилировать")
        compile_action = compile_menu.addAction("Запустить компиляцию")
        compile_action.triggered.connect(self.on_compile)

        # Меню «Тест»
        test_menu = menu_bar.addMenu("Тест")
        test_action = test_menu.addAction("Запустить тесты")
        test_action.triggered.connect(self.on_test)

    @Slot()
    def on_compile(self):
        """Запросить запуск компилятора формы"""
        app_signals.menu_signals.request_compile.emit()

    @Slot()
    def on_test(self):
        """Заглушка для действия «Тест»"""
        print("Запускаются тесты...")

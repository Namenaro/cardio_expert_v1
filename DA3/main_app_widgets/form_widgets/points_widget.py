from typing import List

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QMessageBox, QScrollArea, QSizePolicy
)

from CORE.db_dataclasses import Point
from DA3 import app_signals
from DA3.base_widget import BaseWidget


class PointsWidget(BaseWidget):
    """Виджет для работы с точками формы"""

    def __init__(self):
        super().__init__()
        self._points: List[Point] = []
        self.setup_ui()
        self.apply_styles("common.qss", "points_widget.qss")

    def setup_ui(self):
        # Основной layout - уменьшенные отступы
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Заголовок
        title_label = QLabel("Точки формы")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setObjectName("mainTitle")
        main_layout.addWidget(title_label)

        # Область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("border: none;")

        # Контейнер для списка точек
        self.points_container = QWidget()
        self.points_container.setObjectName("pointsContainer")
        self.points_layout = QVBoxLayout(self.points_container)
        self.points_layout.setSpacing(4)
        self.points_layout.setContentsMargins(4, 4, 4, 4)
        self.points_layout.addStretch()

        scroll_area.setWidget(self.points_container)
        main_layout.addWidget(scroll_area)

        # Кнопка добавления
        self.add_button = QPushButton("Добавить точку")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.on_add_point_clicked)
        self.add_button.setMinimumHeight(32)

        main_layout.addWidget(self.add_button)

    def reset_points(self, points: List[Point]) -> None:
        """Установить новый список точек"""
        self._points = points
        self.refresh()

    def refresh(self) -> None:
        """Обновить отображение списка точек"""
        # Очищаем текущий список
        while self.points_layout.count() > 1:
            item = self.points_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Добавляем виджеты для каждой точки
        for point in self._points:
            self._add_point_widget(point)

    def _add_point_widget(self, point: Point) -> None:
        """Создать и добавить виджет для одной точки"""
        # Фрейм для точки
        point_frame = QFrame()
        point_frame.setObjectName("pointFrame")
        point_frame.setFrameShape(QFrame.Shape.NoFrame)
        point_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Layout для фрейма - горизонтальный
        frame_layout = QHBoxLayout(point_frame)
        frame_layout.setContentsMargins(10, 8, 10, 8)
        frame_layout.setSpacing(10)

        # === ЛЕВАЯ ЧАСТЬ: ID и название ===
        left_layout = QHBoxLayout()
        left_layout.setSpacing(8)

        # ID точки
        id_text = f"ID{point.id if point.id is not None else '?'}"
        id_label = QLabel(id_text)
        id_label.setObjectName("idLabel")
        left_layout.addWidget(id_label)

        # Название точки
        name_text = point.name if point.name else "<Название не указано>"
        name_label = QLabel(name_text)
        name_label.setObjectName("pointNameLabel")
        left_layout.addWidget(name_label)

        frame_layout.addLayout(left_layout)

        # Пустое пространство
        frame_layout.addStretch()

        # === ПРАВАЯ ЧАСТЬ: Кнопки ===
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        # Кнопка редактирования
        edit_button = QPushButton("Редактировать")
        edit_button.setObjectName("editPointButton")
        edit_button.clicked.connect(lambda checked, p=point: self.on_edit_point_clicked(p))
        buttons_layout.addWidget(edit_button)

        # Кнопка удаления
        delete_button = QPushButton("Удалить")
        delete_button.setObjectName("deletePointButton")
        delete_button.clicked.connect(lambda checked, p=point: self.on_delete_point_clicked(p))
        buttons_layout.addWidget(delete_button)

        frame_layout.addLayout(buttons_layout)

        # Добавляем фрейм
        self.points_layout.insertWidget(self.points_layout.count() - 1, point_frame)

    @Slot(Point)
    def on_edit_point_clicked(self, point: Point) -> None:
        """Обработчик нажатия кнопки редактирования точки"""
        app_signals.point.request_point_redactor.emit(point)

    @Slot(Point)
    def on_delete_point_clicked(self, point: Point) -> None:
        """Обработчик нажатия кнопки удаления точки"""
        if point.id is None:
            QMessageBox.warning(self, "Ошибка", "Точка не сохранена в базе данных")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Удалить точку '{point.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            app_signals.point.db_delete_point.emit(point)

    @Slot()
    def on_add_point_clicked(self) -> None:
        """Обработчик нажатия кнопки добавления новой точки"""
        new_point = Point()
        app_signals.point.request_point_redactor.emit(new_point)
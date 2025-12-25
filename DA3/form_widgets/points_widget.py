from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QMessageBox, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from CORE.db_dataclasses import Point
from DA3 import app_signals


class PointsWidget(QWidget):
    """Виджет для работы с точками формы"""

    def __init__(self):
        super().__init__()
        self._points: List[Point] = []
        self.setup_ui()

    def setup_ui(self):
        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title_label = QLabel("Точки формы")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Область прокрутки для списка точек
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Контейнер для списка точек
        self.points_container = QWidget()
        self.points_layout = QVBoxLayout(self.points_container)
        self.points_layout.setSpacing(5)
        self.points_layout.setContentsMargins(5, 5, 5, 5)
        self.points_layout.addStretch()

        scroll_area.setWidget(self.points_container)
        main_layout.addWidget(scroll_area)

        # Кнопка добавления новой точки
        self.add_button = QPushButton("Добавить точку")
        self.add_button.clicked.connect(self.on_add_point_clicked)
        self.add_button.setMinimumHeight(40)
        main_layout.addWidget(self.add_button)

        self.setStyleSheet("background-color: #e6ffe6;")

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
        point_frame.setFrameShape(QFrame.Shape.Box)
        point_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Layout для фрейма
        frame_layout = QHBoxLayout(point_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)

        # Информация о точке
        info_text = f"{point.name}"
        if point.id is not None:
            info_text = f"ID{point.id}: {info_text}"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold;")
        frame_layout.addWidget(info_label)

        # Пустое пространство
        frame_layout.addStretch()

        # Кнопка редактирования
        edit_button = QPushButton("Редактировать")
        edit_button.clicked.connect(lambda checked, p=point: self.on_edit_point_clicked(p))
        frame_layout.addWidget(edit_button)

        # Кнопка удаления
        delete_button = QPushButton("Удалить")
        delete_button.clicked.connect(lambda checked, p=point: self.on_delete_point_clicked(p))
        frame_layout.addWidget(delete_button)

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
            # Испускаем сигнал с объектом Point
            app_signals.point.db_delete_point.emit(point)

    @Slot(Point)
    def on_add_point_clicked(self) -> None:
        """Обработчик нажатия кнопки добавления новой точки"""
        # Создаем новую точку и отправляем в редактор
        new_point = Point()
        app_signals.point.request_point_redactor.emit(new_point)
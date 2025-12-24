# ui/magnifier_widget.py
from PySide6.QtGui import QPixmap, QPainter, QPen
from PySide6.QtCore import Qt, QRectF, Signal as PySideSignal

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Signal as PySideSignal, QRectF
from PySide6.QtGui import QPixmap, QPainter, QPen

class MagnifierWidget(QWidget):
    """
    Виджет-лупа, который теперь умеет обновлять свое содержимое.
    """
    point_placed = PySideSignal(float)

    def __init__(self, scale_factor: int = 3):
        super().__init__()
        
        self.scale_factor = scale_factor
        self.data_rect = QRectF()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.ToolTip)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.image_label = QLabel()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

    def update_content(self, pixmap_fragment: QPixmap, data_rect: QRectF):
        """Обновляет изображение и связанные с ним данные."""
        self.data_rect = data_rect
        scaled_pixmap = pixmap_fragment.scaled(
            pixmap_fragment.width() * self.scale_factor,
            pixmap_fragment.height() * self.scale_factor,
        )
        
        painter_pixmap = QPixmap(scaled_pixmap.size())
        painter_pixmap.fill(Qt.transparent)
        p = QPainter(painter_pixmap)
        p.drawPixmap(0, 0, scaled_pixmap)
        p.setPen(QPen(Qt.red, 1))
        cx, cy = painter_pixmap.width() / 2, painter_pixmap.height() / 2
        p.drawLine(int(cx - 10), int(cy), int(cx + 10), int(cy))
        p.drawLine(int(cx), int(cy - 10), int(cx), int(cy + 10))
        p.end()
        self.image_label.setPixmap(painter_pixmap)
        self.adjustSize()

    def mousePressEvent(self, event):
        """Вызывается при клике внутри лупы."""
        if event.button() == Qt.LeftButton:
            rel_x = event.position().x() / self.width()
            precise_time = self.data_rect.left() + rel_x * self.data_rect.width()
            self.point_placed.emit(precise_time)
            self.close()
        else:
            self.close()
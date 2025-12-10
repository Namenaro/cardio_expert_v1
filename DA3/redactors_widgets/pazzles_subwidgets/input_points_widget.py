from typing import List, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QComboBox
)
from PySide6.QtCore import Qt, Signal
from CORE.db_dataclasses import *


class InputPointsWidget(QWidget):
    """Виджет для редактирования входных параметров объекта"""

    def __init__(self, parent=None):
        super().__init__(parent)
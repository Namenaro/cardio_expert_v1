from PyQt6.QtWidgets import QDialog

from CORE.db_dataclasses import Track


class TrackRedactor(QDialog):
    def __init__(self, parent):
        super().__init__(parent=parent)


    def refresh(self, track:Track):
        pass


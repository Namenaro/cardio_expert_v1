from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    """Глобальные сигналы приложения"""

    # Сигнал для запроса редактора основной информации о форме
    request_main_info_redactor = Signal(object, object)  # Form, sender_widget
    request_point_redactor = Signal(object, object)  # Point или None, sender_widget

    try_delete_point = Signal(int)  # point_id
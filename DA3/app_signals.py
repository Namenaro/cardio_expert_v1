from PySide6.QtCore import QObject, Signal


class AppSignals(QObject):
    """Глобальные сигналы приложения"""

    # Сигнал для запроса редактора основной информации о форме
    request_main_info_redactor = Signal(object, object)  # Form, sender_widget
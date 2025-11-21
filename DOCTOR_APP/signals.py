from PySide6.QtCore import QObject, Signal


class FormSignals(QObject):
    # Сигналы для точек
    requested_point_redaction = Signal(int)  # point_id
    requested_point_addition = Signal()
    requested_point_deletion = Signal(int)  # point_id

    # Сигналы для параметров
    requested_parameter_redaction = Signal(int)  # parameter_id
    requested_parameter_addition = Signal()
    requested_parameter_deletion = Signal(int)  # parameter_id

    # Сигналы для резюме формы
    requested_form_redaction = Signal()

    # Сигналы обновления
    form_updated = Signal(object)  # Form object

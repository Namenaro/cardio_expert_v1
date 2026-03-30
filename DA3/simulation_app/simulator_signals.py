from PySide6.QtCore import Signal, QObject


class SimulatorSignals(QObject):
    """
    Класс-контейнер для всех внутренних сигналов симулятора.
    """

    # Сигналы для выбора элементов формы
    step_selected = Signal(int, int)  # (step_id, num_in_form)
    track_selected = Signal(int)  # (track_id)
    SM_selected = Signal(int, int)  # (SM_id, num_in_track)
    PS_selected = Signal(int)  # (PS_id)

    # Сигналы для навигации по датасету
    requested_next = Signal()  # запрос следующего примера
    requested_prev = Signal()  # запрос предыдущего примера


# Создаем глобальный экземпляр для использования во всем приложении
_signals_instance = None


def get_signals():
    """
    Возвращает глобальный экземпляр сигналов.
    Создает его при первом вызове.
    """
    global _signals_instance
    if _signals_instance is None:
        _signals_instance = SimulatorSignals()
    return _signals_instance

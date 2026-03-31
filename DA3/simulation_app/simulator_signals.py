# DA3/simulation_app/simulator_signals.py

from PySide6.QtCore import Signal, QObject


class SimulatorSignals(QObject):
    """
    Класс-контейнер для сигналов симулятора.
    """

    # Сигналы для выбора элементов формы
    track_selected = Signal(int)  # (track_id)
    step_selected = Signal(int, int)  # (step_id, num_in_form)

    # Сигналы для навигации по датасету
    requested_next = Signal()
    requested_prev = Signal()

    # Сигналы для симуляции
    full_simulate_requested = Signal()
    clear_selection_requested = Signal()
    error_occurred = Signal(str)


_signals_instance = None


def get_signals():
    global _signals_instance
    if _signals_instance is None:
        _signals_instance = SimulatorSignals()
    return _signals_instance
import matplotlib.pyplot as plt
from typing import Optional, List
from CORE.signal_1d import Signal
from CORE.visual_debug.plt_visualisation.helpers.drawinfg_entities_dataclasses import LineStyle, VerticalLineInfo
from CORE.visual_debug.plt_visualisation.helpers.popup_window import PopupWindow
from CORE.visual_debug.plt_visualisation.helpers.renderer import SignalRenderer


class Drawer:
    """
    Основной класс для визуализации сигналов.
    """

    def __init__(self, ax: plt.Axes):
        self.ax = ax
        self.renderer = SignalRenderer()
        self.popup: Optional[PopupWindow] = None

        self.ax.figure.canvas.mpl_connect('button_press_event', self._on_click)

    def add_signal(self, signal: Signal, color='#202020', name: Optional[str] = None):
        self.renderer.add_signal(signal, color, name)

    def add_vertical_line(self, x: float, y_min: float, y_max: float,
                          color: str = 'red', style: LineStyle = LineStyle.SOLID,
                          label: Optional[str] = None, sub_label: Optional[str] = None):
        self.renderer.add_vertical_line(x, y_min, y_max, color, style, label, sub_label)

    def add_vertical_lines_group(self, lines: List[VerticalLineInfo], color: str,
                                 label: Optional[str] = None):
        self.renderer.add_vertical_lines_group(lines, color, label)

    def add_interval(self, left: float, right: float, color: str = 'yellow',
                     alpha: Optional[float] = None, label: Optional[str] = None):
        self.renderer.add_interval(left, right, color, alpha, label)

    def add_point(self, x: float, y: float, color: str = 'red', label: Optional[str] = None,
                  show_label_near_point: bool = False, zorder: int = 5):
        self.renderer.add_point(x, y, color, label, show_label_near_point, zorder)

    def add_segment(self, x1: float, y1: float, x2: float, y2: float,
                    color: str = 'blue', style: LineStyle = LineStyle.SOLID,
                    label: Optional[str] = None, zorder: int = 4):
        self.renderer.add_segment(x1, y1, x2, y2, color, style, label, zorder)

    def redraw(self):
        """Перерисовывает основной график."""
        self.renderer.draw(self.ax)

    def _on_click(self, event):
        """Обработчик кликов."""
        if event.inaxes != self.ax or event.button != 1:
            return
        self._show_popup()

    def _show_popup(self):
        """Показывает всплывающее окно."""
        if self.popup and self.popup.is_alive():
            self.popup.update_content()
        else:
            self.popup = PopupWindow(self.renderer, self._on_popup_closed)
            self.popup.show()

    def _on_popup_closed(self):
        """Вызывается при закрытии попапа."""
        self.redraw()
        self.popup = None


# Пример использования (без изменений)
if __name__ == "__main__":
    from CORE.datasets_wrappers.LUDB import LUDB, LEADS_NAMES

    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 1.9)

    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax)

    drawer.add_signal(signal, color='blue', name='Тестовый сигнал')

    drawer.add_vertical_line(x=0.5, y_min=0.2, y_max=0.8,
                             color='green', style=LineStyle.SOLID,
                             label='R', sub_label='peak')

    group_lines = [
        VerticalLineInfo(x=0.7, y_min=0.3, y_max=0.7,
                         style=LineStyle.SOLID, label='T', sub_label='wave'),
        VerticalLineInfo(x=0.9, y_min=0.25, y_max=0.75,
                         style=LineStyle.DASHED, label='P', sub_label='onset'),
        VerticalLineInfo(x=1.0, y_min=0.3, y_max=0.7,
                         style=LineStyle.DASHED, label='S', sub_label='offset')
    ]
    drawer.add_vertical_lines_group(group_lines, color='red', label='Комплексы QRS')

    drawer.add_interval(left=0.2, right=0.4, color='yellow', alpha=0.3, label='QRS complex')
    drawer.add_interval(left=1.2, right=1.5, color='lightgreen', label='ST segment')

    drawer.redraw()
    plt.tight_layout()
    plt.show()
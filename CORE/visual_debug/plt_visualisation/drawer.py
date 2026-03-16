import matplotlib.pyplot as plt
from typing import Optional, List
from CORE.signal_1d import Signal
from CORE.visual_debug.plt_visualisation.helpers.drawinfg_entities_dataclasses import LineStyle, VerticalLineInfo
from CORE.visual_debug.plt_visualisation.helpers.popup_window import PopupWindow
from CORE.visual_debug.plt_visualisation.helpers.renderer import SignalRenderer


class Drawer:
    """
    Основной класс для визуализации 1-d ЭКГ сигналов на миллиметровке, а также линий и интевалов поверх ЭКГ, с подписями.
    Управляет основным графиком и всплывающим окном.

    :param ax: Объект matplotlib.axes.Axes для отрисовки
    :param is_user_point_needed: Разрешить установку пользовательской точки. По умолчанию True. Получить установленную пользователем точку можно через get_user_point()

    Класс обеспечивает:
        - отрисовку одного или нескольких именованных сигналов на общем графике
        - добавление вертикальных линий с поддержкой основной и дополнительной подписей
        - группировку вертикальных линий с общей записью в легенде
        - выделение участков полупрозрачными интервалами
        - интерактивную пользовательскую точку (одну) с возможностью перетаскивания. Для ее установки надо кликнуть правой кнопкой мыши в попап-окне
        - всплывающее окно с панелью навигации (зум, перетасккивание и т.д.). Для выхова попап-окна нужно кликнуть левой кнопкой мыши по основному ax
    """

    def __init__(self, ax: plt.Axes, is_user_point_needed: bool = True):
        """
        Args:
            ax: Объект Axes для отрисовки
            is_user_point_needed: Флаг, разрешающий установку одной пользовательской точки
        """
        self.ax = ax
        self.renderer = SignalRenderer()
        self.popup: Optional[PopupWindow] = None
        self.is_user_point_needed = is_user_point_needed

        # Подключаем обработчик кликов
        self.ax.figure.canvas.mpl_connect('button_press_event', self._on_click)

    def add_signal(self, signal: Signal, color='#202020', name: Optional[str] = None):
        """Добавляет сигнал для отрисовки."""
        self.renderer.add_signal(signal, color, name)

    def add_vertical_line(self, x: float, y_min: float, y_max: float,
                          color: str = 'red',
                          style: LineStyle = LineStyle.SOLID,
                          label: Optional[str] = None,
                          sub_label: Optional[str] = None):
        """Добавляет одиночную вертикальную линию для отрисовки."""
        self.renderer.add_vertical_line(x, y_min, y_max, color, style, label, sub_label)

    def add_vertical_lines_group(self, lines: List[VerticalLineInfo],
                                 color: str,
                                 label: Optional[str] = None):
        """
        Добавляет группу вертикальных линий для отрисовки.
        Все линии группы рисуются одним цветом и имеют одну общую запись в легенде.

        Args:
            lines: Список объектов VerticalLineInfo (их цвета будут проигнорированы)
            color: Цвет для всех линий группы
            label: Метка группы для легенды
        """
        self.renderer.add_vertical_lines_group(lines, color, label)

    def add_interval(self, left: float, right: float,
                     color: str = 'yellow',
                     alpha: Optional[float] = None,
                     label: Optional[str] = None):
        """
        Добавляет интервал для отрисовки.

        Args:
            left: Левая граница интервала
            right: Правая граница интервала
            color: Цвет заливки
            alpha: Прозрачность (если None, используется глобальная intervals_opacity)
            label: Подпись для легенды
        """
        self.renderer.add_interval(left, right, color, alpha, label)
        # self.redraw()

    def get_user_point(self) -> Optional[float]:
        """Возвращает текущую пользовательскую точку."""
        return self.renderer.get_user_point() if self.is_user_point_needed else None

    def _set_point_by_user(self, x: float):
        """Устанавливает пользовательскую точку и обновляет renderer."""
        if not self.is_user_point_needed:
            return
        self.renderer.set_user_point(x)

    def _on_popup_closed(self):
        """Вызывается при закрытии попап-окна."""

        # Перерисовываем основной график, чтобы показать актуальную точку
        self.redraw()
        # Очищаем ссылку на попап
        self.popup = None

    def _on_click(self, event):
        """Обработчик кликов мыши. Левый клик - открывает всплывающее окно."""
        if event.inaxes != self.ax:
            return

        if event.button == 1:  # Левая кнопка мыши
            self._show_popup_window()

    def _show_popup_window(self):
        """Показывает всплывающее окно."""
        if self.popup is not None and self.popup.is_alive():
            # Если окно уже существует и активно, просто обновляем его содержимое
            self.popup.update_content()
        else:
            # Создаем новое окно, если старого нет или оно закрыто
            self.popup = PopupWindow(
                self.renderer,
                self._set_point_by_user,
                self._on_popup_closed,
                self.is_user_point_needed
            )
            self.popup.show()

    def redraw(self):
        """Перерисовывает основной график."""
        self.renderer.draw(self.ax)

    def add_point(self, x: float, y: float, color: str = 'red', label: Optional[str] = None,
                  show_label_near_point: bool = False, zorder: int = 5):
        """Добавляет точку для отрисовки."""
        self.renderer.add_point(x, y, color, label, show_label_near_point, zorder)

    def add_segment(self, x1: float, y1: float, x2: float, y2: float,
                    color: str = 'blue', style: LineStyle = LineStyle.SOLID,
                    label: Optional[str] = None, zorder: int = 4):
        """Добавляет отрезок для отрисовки."""
        self.renderer.add_segment(x1, y1, x2, y2, color, style, label, zorder)


# Пример использования
if __name__ == "__main__":
    from CORE.datasets_wrappers.LUDB import LUDB, LEADS_NAMES

    # Загружаем тестовый сигнал
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[0], lead_name=LEADS_NAMES.i)
    signal = signal.get_fragment(0.0, 1.9)

    # Создаем основной график
    fig, ax = plt.subplots(figsize=(10, 4))
    drawer = Drawer(ax, is_user_point_needed=True)

    # Добавляем сигнал
    drawer.add_signal(signal, color='blue', name='Тестовый сигнал')

    # Добавляем одиночные вертикальные линии
    drawer.add_vertical_line(x=0.5, y_min=0.2, y_max=0.8,
                             color='green', style=LineStyle.SOLID,
                             label='R', sub_label='peak')

    # Добавляем группу вертикальных линий (все будут красными)
    group_lines = [
        VerticalLineInfo(x=0.7, y_min=0.3, y_max=0.7,
                         style=LineStyle.SOLID, label='T', sub_label='wave'),
        VerticalLineInfo(x=0.9, y_min=0.25, y_max=0.75,
                         style=LineStyle.DASHED, label='P', sub_label='onset'),
        VerticalLineInfo(x=1.0, y_min=0.3, y_max=0.7,
                         style=LineStyle.DASHED, label='S', sub_label='offset')
    ]
    drawer.add_vertical_lines_group(group_lines, color='red', label='Комплексы QRS')

    # Добавляем интервалы для примера
    drawer.add_interval(left=0.2, right=0.4,
                        color='yellow', alpha=0.3,
                        label='QRS complex')

    drawer.add_interval(left=1.2, right=1.5,
                        color='lightgreen',
                        label='ST segment')

    # Отрисовываем все (первый раз)
    drawer.redraw()

    plt.tight_layout()
    plt.show()

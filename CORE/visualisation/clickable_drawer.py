import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from dataclasses import dataclass
from typing import Optional, List, Callable
from enum import Enum
import random
from CORE.signal_1d import Signal


class LineStyle(Enum):
    """Стили линий для вертикальных отметок"""
    SOLID = 'solid'
    DASHED = 'dashed'


@dataclass
class SignalInfo:
    """Хранит информацию о сигнале для отрисовки"""
    signal: Signal
    color: str = '#202020'
    name: Optional[str] = None


@dataclass
class VerticalLineInfo:
    """Хранит информацию о вертикальной линии для отрисовки"""
    x: float
    y_min: float
    y_max: float
    color: str = 'red'
    style: LineStyle = LineStyle.SOLID
    label: Optional[str] = None
    sub_label: Optional[str] = None  # Дополнительная подпись снизу


@dataclass
class IntervalInfo:
    """Хранит информацию об интервале для отрисовки"""
    left: float
    right: float
    color: str = 'yellow'
    alpha: Optional[float] = None  # Если None, используется глобальная прозрачность из SignalRenderer
    label: Optional[str] = None


class SignalRenderer:
    """
    Класс, отвечающий только за логику рисования.
    Хранит контент (сигналы, линии, интервалы) и умеет рисовать их на любом ax.
    """

    def __init__(self):
        self.signals: List[SignalInfo] = []
        self.vertical_lines: List[VerticalLineInfo] = []
        self.intervals: List[IntervalInfo] = []
        self.user_setted_center: Optional[float] = None

        # Настройки миллиметровки
        self.minor_cell_mv = 0.1
        self.minor_cell_sec = 0.04
        self.major_cell_mv = 0.5
        self.major_cell_sec = 0.2
        self.minor_grid_color = "#f4bfbf"
        self.major_grid_color = "#e37373"

        # Настройки для интервалов
        self.intervals_opacity = 0.3  # Глобальная прозрачность для интервалов

        # Настройки для подписей вертикальных линий
        self.label_x_offset = 0.01  # Смещение подписи вправо от линии (в координатах данных)
        self.label_random_range = 0.15  # Диапазон случайного смещения по вертикали (в долях от высоты)

    def add_signal(self, signal: Signal, color='#202020', name: Optional[str] = None):
        """Добавляет сигнал для отрисовки."""
        self.signals.append(SignalInfo(signal, color, name))

    def add_vertical_line(self, x: float, y_min: float, y_max: float,
                          color: str = 'red',
                          style: LineStyle = LineStyle.SOLID,
                          label: Optional[str] = None,
                          sub_label: Optional[str] = None):
        """Добавляет вертикальную линию для отрисовки."""
        self.vertical_lines.append(VerticalLineInfo(x, y_min, y_max, color, style, label, sub_label))

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
        self.intervals.append(IntervalInfo(left, right, color, alpha, label))

    def set_user_point(self, x: float):
        """Устанавливает пользовательскую точку."""
        self.user_setted_center = x

    def get_user_point(self) -> Optional[float]:
        """Возвращает текущую пользовательскую точку."""
        return self.user_setted_center

    def draw(self, ax: plt.Axes):
        """
        Рисует все содержимое на указанном ax.

        Args:
            ax: Объект Axes для отрисовки
        """
        # Очищаем текущий axes
        ax.clear()

        # Сначала рисуем интервалы (чтобы они были на заднем плане)
        for interval_info in self.intervals:
            # Определяем прозрачность
            alpha = interval_info.alpha if interval_info.alpha is not None else self.intervals_opacity

            # Создаем полупрозрачную область во всю высоту графика
            span = ax.axvspan(interval_info.left, interval_info.right,
                              alpha=alpha,
                              color=interval_info.color,
                              label=interval_info.label)

            # Устанавливаем zorder низкий, чтобы интервалы были под сигналами и линиями
            span.set_zorder(1)

        # Затем рисуем сигналы (средний план)
        for signal_info in self.signals:
            time = signal_info.signal.time
            values = signal_info.signal.signal_mv
            ax.plot(time, values,
                    color=signal_info.color,
                    label=signal_info.name,
                    zorder=2)

        # Затем вертикальные линии (передний план) с подписями
        for line_info in self.vertical_lines:
            # Рисуем вертикальную линию
            line = ax.axvline(x=line_info.x,
                              ymin=line_info.y_min,
                              ymax=line_info.y_max,
                              color=line_info.color,
                              linestyle=line_info.style.value,
                              zorder=3)

            # Добавляем подписи, если они есть
            if line_info.label or line_info.sub_label:
                self._add_vertical_line_labels(ax, line_info)

        # Пользовательская точка (самый передний план)
        if self.user_setted_center is not None:
            user_line = ax.axvline(x=self.user_setted_center,
                                   color='black',
                                   linewidth=2,
                                   linestyle='--',
                                   label='Центр пользователя',
                                   zorder=4)

        # Настройка внешнего вида
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, мВ')

        ax.set_aspect(self.minor_cell_sec / self.minor_cell_mv)

        ax.xaxis.set_major_locator(MultipleLocator(self.major_cell_sec))
        ax.xaxis.set_minor_locator(MultipleLocator(self.minor_cell_sec))

        ax.yaxis.set_major_locator(MultipleLocator(self.major_cell_mv))
        ax.yaxis.set_minor_locator(MultipleLocator(self.minor_cell_mv))

        ax.grid(True, 'major', color=self.major_grid_color, zorder=0)
        ax.grid(True, 'minor', color=self.minor_grid_color, linewidth=0.5, zorder=0)

        # Добавляем легенду если есть подписи
        has_labels = (any(s.name for s in self.signals) or
                      any(l.label for l in self.vertical_lines) or
                      any(i.label for i in self.intervals) or
                      self.user_setted_center is not None)
        if has_labels:
            ax.legend()

        # Обновляем отображение
        ax.figure.canvas.draw_idle()

    def _add_vertical_line_labels(self, ax: plt.Axes, line_info: VerticalLineInfo):
        """
        Добавляет подписи к вертикальной линии со случайным позиционированием.

        Args:
            ax: Объект Axes для отрисовки
            line_info: Информация о вертикальной линии
        """
        # Получаем текущие пределы по y
        y_limits = ax.get_ylim()
        y_min_total, y_max_total = y_limits

        # Вычисляем высоту графика
        y_height = y_max_total - y_min_total

        # Вычисляем позиции для подписей на основе y_min и y_max линии
        # Преобразуем относительные координаты (0-1) в абсолютные
        y_line_min = y_min_total + line_info.y_min * y_height
        y_line_max = y_min_total + line_info.y_max * y_height
        y_line_height = y_line_max - y_line_min

        # Позиция для главной подписи (верхняя половина линии)
        if line_info.label:
            # Случайная позиция в верхней половине линии (от середины до верха)
            y_label_pos = y_line_min + y_line_height * (0.5 + random.uniform(0, 0.5))

            # Добавляем главную подпись
            ax.text(line_info.x + self.label_x_offset, y_label_pos,
                    line_info.label,
                    fontsize=9,
                    color=line_info.color,
                    verticalalignment='center',
                    horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2',
                              facecolor='white',
                              edgecolor='none',
                              alpha=0.7),
                    zorder=4)

        # Позиция для дополнительной подписи (нижняя половина линии)
        if line_info.sub_label:
            # Случайная позиция в нижней половине линии (от низа до середины)
            y_sub_label_pos = y_line_min + y_line_height * random.uniform(0, 0.5)

            # Добавляем дополнительную подпись
            ax.text(line_info.x + self.label_x_offset, y_sub_label_pos,
                    line_info.sub_label,
                    fontsize=8,
                    color=line_info.color,
                    style='italic',
                    verticalalignment='center',
                    horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2',
                              facecolor='white',
                              edgecolor='none',
                              alpha=0.7),
                    zorder=4)


class PopupWindow:
    """
    Класс, управляющий всплывающим окном.
    Получает renderer в конструктор и отображает его содержимое.
    """

    def __init__(self, renderer: SignalRenderer, on_user_point_set: Callable[[float], None],
                 on_closing: Optional[Callable[[], None]] = None,
                 is_user_point_needed: bool = True):
        """
        Args:
            renderer: Объект SignalRenderer с данными для отображения
            on_user_point_set: Функция, вызываемая при установке пользовательской точки
            on_closing: Функция, вызываемая при закрытии окна
            is_user_point_needed: Флаг, разрешающий установку пользовательской точки
        """
        self.renderer = renderer
        self.on_user_point_set = on_user_point_set
        self.on_closing = on_closing
        self.is_user_point_needed = is_user_point_needed
        self.window = None
        self.fig = None
        self.ax = None
        self.canvas = None
        self.user_line = None
        self.dragging = False
        self.drag_start_x = None

    def show(self):
        """Показывает всплывающее окно."""
        if self.window is not None:
            try:
                self.window.lift()
                return
            except:
                self._cleanup()

        import tkinter as tk
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        # Создаем новое окно и фигуру
        self.fig, self.ax = plt.subplots(figsize=(12, 6))

        # Отрисовываем содержимое
        self._draw_content()

        # Создаем корневое окно tkinter
        self.window = tk.Tk()
        self.window.title("Увеличенный вид сигнала")
        self.window.protocol("WM_DELETE_WINDOW", self._on_popup_closing)

        # Создаем canvas для отображения графика
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Добавляем панель навигации
        toolbar = NavigationToolbar2Tk(self.canvas, self.window)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Подключаем обработчики мыши для перетаскивания (только если нужна пользовательская точка)
        if self.is_user_point_needed:
            self.fig.canvas.mpl_connect('button_press_event', self._on_mouse_press)
            self.fig.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
            self.fig.canvas.mpl_connect('button_release_event', self._on_mouse_release)

        # Настраиваем и показываем окно
        self.fig.tight_layout()
        self.window.mainloop()

    def _draw_content(self):
        """Отрисовывает содержимое без полной очистки."""
        self.ax.clear()

        # Сначала рисуем интервалы
        for interval_info in self.renderer.intervals:
            alpha = interval_info.alpha if interval_info.alpha is not None else self.renderer.intervals_opacity
            span = self.ax.axvspan(interval_info.left, interval_info.right,
                                   alpha=alpha,
                                   color=interval_info.color,
                                   label=interval_info.label,
                                   zorder=1)

        # Затем сигналы
        for signal_info in self.renderer.signals:
            time = signal_info.signal.time
            values = signal_info.signal.signal_mv
            self.ax.plot(time, values,
                         color=signal_info.color,
                         label=signal_info.name,
                         zorder=2)

        # Затем вертикальные линии с подписями
        for line_info in self.renderer.vertical_lines:
            # Рисуем вертикальную линию
            self.ax.axvline(x=line_info.x,
                            ymin=line_info.y_min,
                            ymax=line_info.y_max,
                            color=line_info.color,
                            linestyle=line_info.style.value,
                            zorder=3)

            # Добавляем подписи, если они есть
            if line_info.label or line_info.sub_label:
                self._add_vertical_line_labels(line_info)

        # Настройка внешнего вида
        self.ax.set_xlabel('Время, с')
        self.ax.set_ylabel('Амплитуда, мВ')
        self.ax.set_aspect(self.renderer.minor_cell_sec / self.renderer.minor_cell_mv)

        self.ax.xaxis.set_major_locator(MultipleLocator(self.renderer.major_cell_sec))
        self.ax.xaxis.set_minor_locator(MultipleLocator(self.renderer.minor_cell_sec))

        self.ax.yaxis.set_major_locator(MultipleLocator(self.renderer.major_cell_mv))
        self.ax.yaxis.set_minor_locator(MultipleLocator(self.renderer.minor_cell_mv))

        self.ax.grid(True, 'major', color=self.renderer.major_grid_color, zorder=0)
        self.ax.grid(True, 'minor', color=self.renderer.minor_grid_color, linewidth=0.5, zorder=0)

        # Отрисовываем пользовательскую точку если она установлена и нужна
        if self.is_user_point_needed and self.renderer.user_setted_center is not None:
            self.user_line = self.ax.axvline(x=self.renderer.user_setted_center,
                                             color='black',
                                             linewidth=2,
                                             linestyle='--',
                                             label='Центр пользователя',
                                             zorder=4)
        else:
            self.user_line = None

        # Добавляем легенду если есть подписи
        has_labels = (any(s.name for s in self.renderer.signals) or
                      any(l.label for l in self.renderer.vertical_lines) or
                      any(i.label for i in self.renderer.intervals) or
                      (self.is_user_point_needed and self.renderer.user_setted_center is not None))
        if has_labels:
            self.ax.legend()

    def _add_vertical_line_labels(self, line_info: VerticalLineInfo):
        """
        Добавляет подписи к вертикальной линии со случайным позиционированием.

        Args:
            line_info: Информация о вертикальной линии
        """
        # Получаем текущие пределы по y
        y_limits = self.ax.get_ylim()
        y_min_total, y_max_total = y_limits

        # Вычисляем высоту графика
        y_height = y_max_total - y_min_total

        # Вычисляем позиции для подписей на основе y_min и y_max линии
        y_line_min = y_min_total + line_info.y_min * y_height
        y_line_max = y_min_total + line_info.y_max * y_height
        y_line_height = y_line_max - y_line_min

        # Позиция для главной подписи (верхняя половина линии)
        if line_info.label:
            # Случайная позиция в верхней половине линии (от середины до верха)
            y_label_pos = y_line_min + y_line_height * (0.5 + random.uniform(0, 0.5))

            # Добавляем главную подпись
            self.ax.text(line_info.x + self.renderer.label_x_offset, y_label_pos,
                         line_info.label,
                         fontsize=9,
                         color=line_info.color,
                         verticalalignment='center',
                         horizontalalignment='left',
                         bbox=dict(boxstyle='round,pad=0.2',
                                   facecolor='white',
                                   edgecolor='none',
                                   alpha=0.7),
                         zorder=4)

        # Позиция для дополнительной подписи (нижняя половина линии)
        if line_info.sub_label:
            # Случайная позиция в нижней половине линии (от низа до середины)
            y_sub_label_pos = y_line_min + y_line_height * random.uniform(0, 0.5)

            # Добавляем дополнительную подпись
            self.ax.text(line_info.x + self.renderer.label_x_offset, y_sub_label_pos,
                         line_info.sub_label,
                         fontsize=8,
                         color=line_info.color,
                         style='italic',
                         verticalalignment='center',
                         horizontalalignment='left',
                         bbox=dict(boxstyle='round,pad=0.2',
                                   facecolor='white',
                                   edgecolor='none',
                                   alpha=0.7),
                         zorder=4)

    def _update_user_line(self, x: float):
        """Обновляет позицию пользовательской линии без полной перерисовки."""
        if not self.is_user_point_needed:
            return

        if self.user_line:
            try:
                # Удаляем старую линию
                self.user_line.remove()
            except:
                pass

        # Создаем новую линию
        self.user_line = self.ax.axvline(x=x,
                                         color='black',
                                         linewidth=2,
                                         linestyle='--',
                                         zorder=4)

        # Обновляем renderer
        self.renderer.set_user_point(x)

        # Перерисовываем только canvas
        self.fig.canvas.draw_idle()

    def _on_mouse_press(self, event):
        """Обработчик нажатия кнопки мыши."""
        if not self.is_user_point_needed or event.inaxes != self.ax:
            return

        # Правая кнопка - установка точки
        if event.button == 3:
            self._update_user_line(event.xdata)
            self.on_user_point_set(event.xdata)

        # Левая кнопка - начало перетаскивания (если кликнули близко к линии)
        elif event.button == 1 and self.user_line and self.renderer.user_setted_center is not None:
            # Проверяем, кликнули ли рядом с линией (в пределах 0.02 по оси X)
            if abs(event.xdata - self.renderer.user_setted_center) < 0.02:
                self.dragging = True
                self.drag_start_x = event.xdata

    def _on_mouse_move(self, event):
        """Обработчик движения мыши."""
        if not self.is_user_point_needed or not self.dragging or event.inaxes != self.ax:
            return

        # Обновляем позицию линии при перетаскивании
        self._update_user_line(event.xdata)
        self.on_user_point_set(event.xdata)

    def _on_mouse_release(self, event):
        """Обработчик отпускания кнопки мыши."""
        if self.dragging:
            self.dragging = False
            self.drag_start_x = None

    def _on_popup_closing(self):
        """Вызывается при закрытии попап-окна."""
        # Вызываем колбэк закрытия, если он есть
        if self.on_closing:
            self.on_closing()
        self._cleanup()

    def _cleanup(self):
        """Очищает ресурсы при закрытии окна."""
        if self.window:
            self.window.destroy()
            self.window = None
            self.fig = None
            self.ax = None
            self.canvas = None
            self.user_line = None

    def update_content(self):
        """Обновляет содержимое окна."""
        if self.window is not None and self.ax is not None:
            self._draw_content()
            self.fig.canvas.draw_idle()
            self.window.lift()  # Поднимаем окно наверх

    def is_alive(self) -> bool:
        """Проверяет, активно ли окно."""
        return self.window is not None


class Signal_1D_Drawer:
    """
    Основной класс для визуализации 1-d сигналов.
    Управляет основным графиком и всплывающим окном.
    """

    def __init__(self, ax: plt.Axes, is_user_point_needed: bool = True):
        """
        Args:
            ax: Объект Axes для отрисовки
            is_user_point_needed: Флаг, разрешающий установку пользовательской точки
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
        self.redraw()

    def add_vertical_line(self, x: float, y_min: float, y_max: float,
                          color: str = 'red',
                          style: LineStyle = LineStyle.SOLID,
                          label: Optional[str] = None,
                          sub_label: Optional[str] = None):
        """Добавляет вертикальную линию для отрисовки."""
        self.renderer.add_vertical_line(x, y_min, y_max, color, style, label, sub_label)
        self.redraw()

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
        self.redraw()

    def get_user_point(self) -> Optional[float]:
        """Возвращает текущую пользовательскую точку."""
        return self.renderer.get_user_point() if self.is_user_point_needed else None

    def _set_point_by_user(self, x: float):
        """Устанавливает пользовательскую точку и обновляет renderer."""
        if not self.is_user_point_needed:
            return
        print(f"Установлена пользовательская точка: {x:.3f}")
        self.renderer.set_user_point(x)
        # Не перерисовываем основной график сразу

    def _on_popup_closed(self):
        """Вызывается при закрытии попап-окна."""
        print("Попап-окно закрыто")
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
    drawer = Signal_1D_Drawer(ax, is_user_point_needed=True)

    # Добавляем сигнал
    drawer.add_signal(signal, color='blue', name='Тестовый сигнал')

    # Добавляем вертикальные линии с подписями
    drawer.add_vertical_line(x=0.5, y_min=0.2, y_max=0.8,
                             color='green', style=LineStyle.SOLID,
                             label='R', sub_label='peak')

    drawer.add_vertical_line(x=0.7, y_min=0.3, y_max=0.7,
                             color='orange', style=LineStyle.SOLID,
                             label='T', sub_label='wave')

    drawer.add_vertical_line(x=0.9, y_min=0.25, y_max=0.75,
                             color='purple', style=LineStyle.DASHED,
                             label='P', sub_label='onset')

    drawer.add_vertical_line(x=1.0, y_min=0.3, y_max=0.7,
                             color='red', style=LineStyle.DASHED,
                             label='S', sub_label='offset')

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
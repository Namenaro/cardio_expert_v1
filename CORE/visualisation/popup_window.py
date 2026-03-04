import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from typing import Optional, List, Callable, Union

from CORE.visualisation.renderer import SignalRenderer


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
        self.fig, self.ax = plt.subplots(figsize=(16, 8))

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

        # Затем одиночные вертикальные линии
        for line_info in self.renderer.vertical_lines:
            self.renderer._draw_vertical_line(self.ax, line_info)

        # Затем группы вертикальных линий
        legend_elements = []
        for group_info in self.renderer.vertical_line_groups:
            for line_info in group_info.lines:
                self.renderer._draw_vertical_line(self.ax, line_info)

            if group_info.label:
                from matplotlib.lines import Line2D
                legend_elements.append(Line2D([0], [0],
                                              color=group_info.color,
                                              linestyle='-',
                                              label=group_info.label))

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

        # Добавляем легенду
        current_handles, current_labels = self.ax.get_legend_handles_labels()
        all_handles = list(current_handles) + legend_elements

        if all_handles:
            self.ax.legend(handles=all_handles)

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

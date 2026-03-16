import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from typing import Optional, Callable

from CORE.visual_debug.plt_visualisation.helpers.renderer import SignalRenderer


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
            self._draw_vertical_line(self.ax, line_info)

        # Затем группы вертикальных линий
        legend_elements = []
        for group_info in self.renderer.vertical_line_groups:
            for line_info in group_info.lines:
                self._draw_vertical_line(self.ax, line_info)

            if group_info.label:
                from matplotlib.lines import Line2D
                legend_elements.append(Line2D([0], [0],
                                              color=group_info.color,
                                              linestyle='-',
                                              label=group_info.label))

        # Рисуем отрезки
        for segment_info in self.renderer.segments:
            self.ax.plot([segment_info.x1, segment_info.x2],
                         [segment_info.y1, segment_info.y2],
                         color=segment_info.color,
                         linestyle=segment_info.style.value,
                         label=segment_info.label,
                         zorder=segment_info.zorder)

        # Рисуем точки
        for point_info in self.renderer.points:
            # Рисуем саму точку
            self.ax.scatter(point_info.x, point_info.y,
                            color=point_info.color,
                            s=50,
                            zorder=point_info.zorder,
                            label=point_info.label if point_info.label and not point_info.show_label_near_point else None)

            # Если нужна подпись рядом с точкой
            if point_info.label and point_info.show_label_near_point:
                # Смещение подписи
                label_offset_x = getattr(self.renderer, 'point_label_offset_x', 0.02)
                label_offset_y = getattr(self.renderer, 'point_label_offset_y', 0.05)

                # Добавляем подпись справа сверху от точки
                self.ax.text(point_info.x + label_offset_x, point_info.y + label_offset_y,
                             point_info.label,
                             fontsize=8,
                             color=point_info.color,
                             verticalalignment='bottom',
                             horizontalalignment='left',
                             bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                                       edgecolor='none', alpha=0.7),
                             zorder=point_info.zorder + 1)

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

    def _draw_vertical_line(self, ax: plt.Axes, line_info):
        """Рисует вертикальную линию и её подписи (скопировано из SignalRenderer)."""
        # Рисуем вертикальную линию
        ax.axvline(x=line_info.x, ymin=line_info.y_min, ymax=line_info.y_max,
                   color=line_info.color,
                   linestyle=line_info.style.value,
                   zorder=3, alpha=0.8)

        # Добавляем подписи, если они есть
        if line_info.label or line_info.sub_label:
            self._add_vertical_line_labels(ax, line_info)

    def _add_vertical_line_labels(self, ax: plt.Axes, line_info):
        """Добавляет подписи к вертикальной линии (скопировано из SignalRenderer)."""
        import random

        # Получаем текущие пределы по y
        y_limits = ax.get_ylim()
        y_min_total, y_max_total = y_limits

        # Вычисляем высоту графика
        y_height = y_max_total - y_min_total

        # Вычисляем позиции для подписей на основе y_min и y_max линии
        y_line_min = y_min_total + line_info.y_min * y_height
        y_line_max = y_min_total + line_info.y_max * y_height
        y_line_height = y_line_max - y_line_min

        # Смещение подписи вправо (можно вынести в параметры renderer)
        label_x_offset = getattr(self.renderer, 'label_x_offset', 0.01)

        # Позиция для главной подписи (верхняя половина линии)
        if line_info.label:
            # Случайная позиция в верхней половине линии (от середины до верха)
            y_label_pos = y_line_min + y_line_height * (0.5 + random.uniform(0, 0.5))

            # Добавляем главную подпись
            ax.text(line_info.x + label_x_offset, y_label_pos, line_info.label,
                    fontsize=9, color=line_info.color,
                    verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                              edgecolor='none', alpha=0.7), zorder=4)

        # Позиция для дополнительной подписи (нижняя половина линии)
        if line_info.sub_label:
            # Случайная позиция в нижней половине линии (от низа до середины)
            y_sub_label_pos = y_line_min + y_line_height * random.uniform(0, 0.5)

            # Добавляем дополнительную подпись
            ax.text(line_info.x + label_x_offset, y_sub_label_pos, line_info.sub_label,
                    fontsize=8, color=line_info.color, style='italic',
                    verticalalignment='center', horizontalalignment='left',
                    bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                              edgecolor='none', alpha=0.7), zorder=4)

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
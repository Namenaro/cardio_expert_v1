import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum
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


class SignalRenderer:
    """
    Класс, отвечающий только за логику рисования.
    Хранит контент (сигналы, линии) и умеет рисовать их на любом ax.
    """

    def __init__(self):
        self.signals: List[SignalInfo] = []
        self.vertical_lines: List[VerticalLineInfo] = []
        self.user_setted_center: Optional[float] = None

        # Настройки миллиметровки
        self.minor_cell_mv = 0.1
        self.minor_cell_sec = 0.04
        self.major_cell_mv = 0.5
        self.major_cell_sec = 0.2
        self.minor_grid_color = "#f4bfbf"
        self.major_grid_color = "#e37373"

    def add_signal(self, signal: Signal, color='#202020', name: Optional[str] = None):
        """Добавляет сигнал для отрисовки."""
        self.signals.append(SignalInfo(signal, color, name))

    def add_vertical_line(self, x: float, y_min: float, y_max: float,
                          color: str = 'red',
                          style: LineStyle = LineStyle.SOLID,
                          label: Optional[str] = None):
        """Добавляет вертикальную линию для отрисовки."""
        self.vertical_lines.append(VerticalLineInfo(x, y_min, y_max, color, style, label))

    def set_user_point(self, x: float):
        """Устанавливает пользовательскую точку."""
        self.user_setted_center = x

    def draw(self, ax: plt.Axes):
        """
        Рисует все содержимое на указанном ax.

        Args:
            ax: Объект Axes для отрисовки
        """
        # Очищаем текущий axes
        ax.clear()

        # Отрисовываем все сигналы
        for signal_info in self.signals:
            time = signal_info.signal.time
            values = signal_info.signal.signal_mv
            ax.plot(time, values,
                    color=signal_info.color,
                    label=signal_info.name)

        # Отрисовываем все вертикальные линии
        for line_info in self.vertical_lines:
            ax.axvline(x=line_info.x,
                       ymin=line_info.y_min,
                       ymax=line_info.y_max,
                       color=line_info.color,
                       linestyle=line_info.style.value,
                       label=line_info.label)

        # Отрисовываем пользовательскую точку если она установлена
        if self.user_setted_center is not None:
            ax.axvline(x=self.user_setted_center,
                       color='black',
                       linewidth=2,
                       linestyle='--',
                       label='Центр пользователя')

        # Настройка внешнего вида
        ax.set_xlabel('Время, с')
        ax.set_ylabel('Амплитуда, мВ')

        ax.set_aspect(self.minor_cell_sec / self.minor_cell_mv)

        ax.xaxis.set_major_locator(MultipleLocator(self.major_cell_sec))
        ax.xaxis.set_minor_locator(MultipleLocator(self.minor_cell_sec))

        ax.yaxis.set_major_locator(MultipleLocator(self.major_cell_mv))
        ax.yaxis.set_minor_locator(MultipleLocator(self.minor_cell_mv))

        ax.grid(True, 'major', color=self.major_grid_color)
        ax.grid(True, 'minor', color=self.minor_grid_color, linewidth=0.5)

        # Добавляем легенду если есть подписи
        has_labels = (any(s.name for s in self.signals) or
                      any(l.label for l in self.vertical_lines) or
                      self.user_setted_center is not None)
        if has_labels:
            ax.legend()

        # Обновляем отображение
        ax.figure.canvas.draw_idle()


class PopupWindow:
    """
    Класс, управляющий всплывающим окном.
    Получает renderer в конструктор и отображает его содержимое.
    """

    def __init__(self, renderer: SignalRenderer, on_user_point_set: callable):
        """
        Args:
            renderer: Объект SignalRenderer с данными для отображения
            on_user_point_set: Функция, вызываемая при установке пользовательской точки
        """
        self.renderer = renderer
        self.on_user_point_set = on_user_point_set
        self.window = None
        self.fig = None
        self.ax = None
        self.canvas = None

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
        self.renderer.draw(self.ax)

        # Создаем корневое окно tkinter
        self.window = tk.Tk()
        self.window.title("Увеличенный вид сигнала")

        # Обработчик закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self._cleanup)

        # Создаем canvas для отображения графика
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Добавляем панель навигации
        toolbar = NavigationToolbar2Tk(self.canvas, self.window)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Подключаем обработчик правого клика
        def on_click(event):
            if event.inaxes == self.ax and event.button == 3:  # Правая кнопка
                self.on_user_point_set(event.xdata)
                # Не закрываем окно, просто обновим содержимое после того,
                # как основной drawer обновит renderer
                self.window.after(100, self.update_content)  # Небольшая задержка для гарантии обновления

        self.fig.canvas.mpl_connect('button_press_event', on_click)

        # Настраиваем и показываем окно
        self.fig.tight_layout()
        self.window.mainloop()

    def _cleanup(self):
        """Очищает ресурсы при закрытии окна."""
        if self.window:
            self.window.destroy()
        self.window = None
        self.fig = None
        self.ax = None
        self.canvas = None

    def update_content(self):
        """Обновляет содержимое окна."""
        if self.window is not None and self.ax is not None:
            self.renderer.draw(self.ax)


class Signal_1D_Drawer:
    """
    Основной класс для визуализации 1-d сигналов.
    Управляет основным графиком и всплывающим окном.
    """

    def __init__(self, ax: plt.Axes):
        self.ax = ax
        self.renderer = SignalRenderer()
        self.popup: Optional[PopupWindow] = None

        # Подключаем обработчик кликов
        self.ax.figure.canvas.mpl_connect('button_press_event', self._on_click)

    def add_signal(self, signal: Signal, color='#202020', name: Optional[str] = None):
        """Добавляет сигнал для отрисовки."""
        self.renderer.add_signal(signal, color, name)
        self.redraw()

    def add_vertical_line(self, x: float, y_min: float, y_max: float,
                          color: str = 'red',
                          style: LineStyle = LineStyle.SOLID,
                          label: Optional[str] = None):
        """Добавляет вертикальную линию для отрисовки."""
        self.renderer.add_vertical_line(x, y_min, y_max, color, style, label)
        self.redraw()

    def _set_point_by_user(self, x: float):
        """Устанавливает пользовательскую точку и обновляет все окна."""
        print(f"Установлена пользовательская точка: {x:.3f}")  # Для отладки
        self.renderer.set_user_point(x)
        self.redraw()

    def _on_click(self, event):
        """Обработчик кликов мыши. Левый клик - открывает всплывающее окно."""
        if event.inaxes != self.ax:
            return

        if event.button == 1:  # Левая кнопка мыши
            self._show_popup_window()

    def _show_popup_window(self):
        """Показывает всплывающее окно."""
        if self.popup is None:
            # Создаем новое окно, передавая ему наш renderer
            self.popup = PopupWindow(self.renderer, self._set_point_by_user)

        # Показываем окно
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
    drawer = Signal_1D_Drawer(ax)

    # Добавляем сигнал
    drawer.add_signal(signal, color='blue', name='Тестовый сигнал')

    # Добавляем вертикальные линии для примера
    drawer.add_vertical_line(x=0.5, y_min=0.2, y_max=0.8,
                             color='green', style=LineStyle.SOLID,
                             label='Сплошная метка')

    drawer.add_vertical_line(x=1.0, y_min=0.3, y_max=0.7,
                             color='red', style=LineStyle.DASHED,
                             label='Штриховая метка')

    # Отрисовываем все (первый раз)
    drawer.redraw()

    plt.tight_layout()
    plt.show()

import matplotlib.pyplot as plt
from typing import Optional, Callable


class PopupWindow:
    """
    Управляет всплывающим окном с увеличенным видом.
    """

    def __init__(self, renderer, on_closing: Optional[Callable[[], None]] = None):
        self.renderer = renderer
        self.on_closing = on_closing

        self.window = None
        self.fig = None
        self.ax = None

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

        self.fig, self.ax = plt.subplots(figsize=(16, 8))
        self.renderer.draw(self.ax)  # Просто вызываем draw у renderer'а

        self.window = tk.Tk()
        self.window.title("Увеличенный вид сигнала")
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)

        canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.fig.tight_layout()
        self.window.mainloop()

    def _on_closing(self):
        """Обработчик закрытия окна."""
        if self.on_closing:
            self.on_closing()
        self._cleanup()

    def _cleanup(self):
        """Очищает ресурсы."""
        if self.window:
            self.window.destroy()
            self.window = None
            self.fig = None
            self.ax = None

    def update_content(self):
        """Обновляет содержимое окна."""
        if self.window and self.ax:
            self.renderer.draw(self.ax)
            self.window.lift()

    def is_alive(self) -> bool:
        return self.window is not None
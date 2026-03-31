# DA3/simulation_app/simulation_widgets/utils.py

import colorsys
from typing import List, Optional

from PySide6.QtWidgets import QTextEdit

from CORE.run import Exemplar


class ExemplarColorManager:
    """
    Менеджер для генерации и хранения цветов экземпляров.
    """

    def __init__(self):
        self._colors = {}

    def generate_color_from_index(self, index: int) -> str:
        """
        Генерирует цвет на основе индекса экземпляра.
        Использует золотое сечение для равномерного распределения.
        """
        golden_ratio = 0.618033988749895
        hue = (index * golden_ratio) % 1.0
        saturation = 0.7
        value = 0.8

        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return f'#{int(rgb[0] * 255):02x}{int(rgb[1] * 255):02x}{int(rgb[2] * 255):02x}'

    def get_color(self, exemplar: Exemplar, index: int) -> str:
        """Возвращает цвет для экземпляра, используя кэш."""
        exemplar_id = id(exemplar)
        if exemplar_id not in self._colors:
            self._colors[exemplar_id] = self.generate_color_from_index(index)
        return self._colors[exemplar_id]

    def get_colors_list(self, exemplars: List[Exemplar]) -> List[str]:
        """Возвращает список цветов для списка экземпляров."""
        return [self.get_color(exemplar, idx) for idx, exemplar in enumerate(exemplars)]

    def get_color_map(self, exemplars: List[Exemplar]) -> dict:
        """Возвращает словарь {exemplar: color}."""
        return {exemplar: self.get_color(exemplar, idx) for idx, exemplar in enumerate(exemplars)}

    def clear(self):
        """Очищает кэш цветов."""
        self._colors.clear()


class ExemplarInfoFormatter:
    """
    Форматтер для отображения информации об экземпляре в HTML.
    """

    def __init__(self):
        pass

    def _get_block_style(self, color: str) -> str:
        """Возвращает стиль для inline-блока."""
        return f'style="color: {color}; display: inline-block; margin-right: 15px;"'

    def _get_badge_style(self, color: str) -> str:
        """Возвращает стиль для бейджа."""
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f'style="color: {color}; background-color: rgba({r}, {g}, {b}, 0.1); padding: 2px 6px; border-radius: 12px; display: inline-block; margin-right: 10px;"'

    def _format_points(self, exemplar: Exemplar) -> str:
        """Форматирует информацию о точках."""
        points_info = []
        for point_name, (x, track_id) in exemplar._points.items():
            points_info.append(f"{point_name}: {x:.3f}с")
        return ", ".join(points_info) if points_info else "нет точек"

    def _format_params(self, exemplar: Exemplar) -> Optional[str]:
        """Форматирует информацию о параметрах."""
        param_names = exemplar.get_param_names()
        if not param_names:
            return None
        params_list = [f"{name}={exemplar.get_parameter_value(name)}" for name in param_names]
        return ", ".join(params_list)

    def _format_failed_hc(self, exemplar: Exemplar) -> str:
        """Форматирует информацию о нарушенных HC."""
        failed_ids = exemplar.get_failed_hc_ids() if hasattr(exemplar, 'get_failed_hc_ids') else []
        if failed_ids:
            return f"❌ HC нарушены: {', '.join(map(str, failed_ids))}"
        return "✅ HC нарушены: нет"

    def _format_passed_hc(self, exemplar: Exemplar) -> str:
        """Форматирует информацию о выполненных HC."""
        passed_ids = exemplar.get_passed_hc_ids() if hasattr(exemplar, 'get_passed_hc_ids') else []
        if passed_ids:
            return f"✓ HC выполнены: {', '.join(map(str, passed_ids))}"
        return "✓ HC выполнены: нет"

    def format_exemplar(self, exemplar: Exemplar, index: int, color: str) -> str:
        """
        Форматирует информацию об экземпляре в HTML.

        :param exemplar: объект Exemplar
        :param index: индекс экземпляра
        :param color: цвет экземпляра в формате hex
        :return: отформатированная HTML-строка
        """
        block_style = self._get_block_style(color)
        badge_style = self._get_badge_style(color)

        parts = []

        # Заголовок
        parts.append(f'<span style="color: {color}; font-weight: bold;">Экземпляр {index + 1}</span>')

        # Оценка
        if exemplar.evaluation_result is not None:
            parts.append(f'<span {badge_style}>оценка: {exemplar.evaluation_result:.3f}</span>')

        # Параметры
        params_str = self._format_params(exemplar)
        if params_str:
            parts.append(f'<span {block_style}>📊 {params_str}</span>')

        # HC нарушены
        parts.append(f'<span {block_style}>{self._format_failed_hc(exemplar)}</span>')

        # HC выполнены
        parts.append(f'<span {block_style}>{self._format_passed_hc(exemplar)}</span>')

        # Точки
        points_str = self._format_points(exemplar)
        parts.append(f'<span {block_style}>📍 Точки: {points_str}</span>')

        return ' '.join(parts)

    def format_exemplars_list(self, exemplars: List[Exemplar], color_manager: ExemplarColorManager) -> str:
        """
        Форматирует список экземпляров в HTML.

        :param exemplars: список экземпляров
        :param color_manager: менеджер цветов
        :return: отформатированная HTML-строка
        """
        if not exemplars:
            return '<i style="color: #999;">Нет созданных экземпляров</i>'

        html_lines = ['<div style="font-family: monospace;">']

        for idx, exemplar in enumerate(exemplars):
            color = color_manager.get_color(exemplar, idx)
            html_lines.append(self.format_exemplar(exemplar, idx, color))
            if idx < len(exemplars) - 1:
                html_lines.append('<hr style="margin: 8px 0; border-color: #ddd;">')

        html_lines.append('</div>')
        return ''.join(html_lines)


class XLimitsCalculator:
    """
    Калькулятор объединенных границ по X для двух рисовалок.
    """

    def __init__(self, padding_percent: float = 20):
        self.padding_percent = padding_percent

    def calculate_combined_limits(self, step_res, draw_step_class, draw_pool_class) -> tuple:
        """
        Рассчитывает объединенные границы по X для DrawStepRes и DrawExemplarsPool.

        :param step_res: объект StepRes
        :param draw_step_class: класс DrawStepRes
        :param draw_pool_class: класс DrawExemplarsPool
        :return: кортеж (left, right) объединенных границ
        """
        import matplotlib.pyplot as plt

        # Создаем временный DrawStepRes для расчета границ
        temp_draw_step = draw_step_class(
            res_obj=step_res,
            exemplar_color_map={},
            padding_percent=self.padding_percent
        )
        step_left, step_right = temp_draw_step._calculate_x_limits()
        plt.close(temp_draw_step.fig)

        # Получаем экземпляры
        exemplars = step_res.get_exemplars()

        if exemplars and len(exemplars) > 0:
            # Создаем временный DrawExemplarsPool для расчета границ
            temp_draw_pool = draw_pool_class(
                exemplars=exemplars,
                padding_percent=self.padding_percent
            )
            # Запускаем сбор точек
            for exemplar in exemplars:
                temp_draw_pool._get_sorted_points_from_exemplar(exemplar)
            pool_left, pool_right = temp_draw_pool._calculate_x_limits()
            plt.close(temp_draw_pool.fig)
        else:
            pool_left, pool_right = step_left, step_right

        # Возвращаем самые широкие границы
        return min(step_left, pool_left), max(step_right, pool_right)


class TextEditHelper:
    """
    Вспомогательный класс для работы с QTextEdit.
    """

    @staticmethod
    def setup_text_edit(text_edit: QTextEdit, max_height: int = 150):
        """
        Настраивает QTextEdit для отображения HTML-текста.

        :param text_edit: виджет QTextEdit
        :param max_height: максимальная высота в пикселях
        """
        text_edit.setMaximumHeight(max_height)
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-family: monospace;
                font-size: 10pt;
                padding: 5px;
            }
        """)

    @staticmethod
    def set_html(text_edit: QTextEdit, html: str):
        """Устанавливает HTML-содержимое в QTextEdit."""
        text_edit.setHtml(html)

    @staticmethod
    def clear(text_edit: QTextEdit):
        """Очищает QTextEdit."""
        text_edit.clear()

import numpy as np
from scipy.fft import fft, ifft, fftfreq, rfft, irfft
from copy import deepcopy
from typing import Optional, Literal
from CORE.signal_1d import Signal


class FrequencyFilter:
    """Фильтрация частот с помощью преобразования Фурье"""

    def __init__(self, cutoff_freq: float = 40.0, filter_type: Literal['lowpass', 'highpass'] = 'lowpass'):
        """
        :param cutoff_freq: Граничная частота в Герцах.
                           Для lowpass - всё ВЫШЕ этой частоты удаляется.
                           Для highpass - всё НИЖЕ этой частоты удаляется.
        :param filter_type: Тип фильтра:
                           'lowpass' - ФНЧ (оставляет низкие частоты, удаляет высокие)
                           'highpass' - ФВЧ (оставляет высокие частоты, удаляет низкие)
        """
        self.cutoff_freq = cutoff_freq
        self.filter_type = filter_type

        # Проверка допустимых значений
        if cutoff_freq <= 0:
            raise ValueError("cutoff_freq должна быть положительным числом")
        if filter_type not in ['lowpass', 'highpass']:
            raise ValueError("filter_type должен быть 'lowpass' или 'highpass'")

    def run(self, signal: Signal, left_t: Optional[float] = None, right_t: Optional[float] = None) -> Signal:
        """
        Применяет частотную фильтрацию к сигналу

        :param signal: Входной сигнал
        :param left_t: Левая граница в секундах (если None - с начала)
        :param right_t: Правая граница в секундах (если None - до конца)
        :return: Отфильтрованный сигнал
        """
        res_signal = deepcopy(signal)
        sampling_rate = res_signal.frequency

        # Проверка частоты среза
        nyquist_freq = sampling_rate / 2
        if self.cutoff_freq >= nyquist_freq:
            raise ValueError(
                f"Частота среза ({self.cutoff_freq} Гц) должна быть меньше частоты Найквиста ({nyquist_freq} Гц)")

        # Определяем границы обрабатываемого участка
        if left_t is not None:
            left_idx = int(left_t * sampling_rate)
        else:
            left_idx = 0

        if right_t is not None:
            right_idx = int(right_t * sampling_rate)
        else:
            right_idx = len(res_signal.signal_mv)

        # Проверяем границы
        left_idx = max(0, left_idx)
        right_idx = min(len(res_signal.signal_mv), right_idx)

        if left_idx >= right_idx:
            return res_signal

        # Выделяем часть сигнала для обработки
        signal_part = np.array(res_signal.signal_mv[left_idx:right_idx])

        # Вычисляем ДПФ
        signal_fft = rfft(signal_part)

        # Получаем соответствующие частоты
        freqs = fftfreq(len(signal_part), 1 / sampling_rate)
        # Для rfft берем только положительные частоты
        freqs_pos = freqs[:len(signal_fft)]

        # Создаем частотную маску в зависимости от типа фильтра
        if self.filter_type == 'lowpass':
            # ФНЧ: оставляем частоты НИЖЕ cutoff_freq
            mask = np.abs(freqs_pos) <= self.cutoff_freq
        else:  # highpass
            # ФВЧ: оставляем частоты ВЫШЕ cutoff_freq
            mask = np.abs(freqs_pos) >= self.cutoff_freq

        # Плавный переход для уменьшения эффекта Гиббса
        # Определяем полосу перехода (например, 10% от cutoff_freq)
        transition_band = 0.1 * self.cutoff_freq

        if self.filter_type == 'lowpass':
            # Для ФНЧ создаем плавный спуск около cutoff_freq
            freq_distance = np.abs(freqs_pos) - self.cutoff_freq
            transition_mask = (freq_distance < 0) & (freq_distance > -transition_band)
            if np.any(transition_mask):
                # Косинусное окно для плавного перехода
                transition_values = 0.5 * (1 + np.cos(np.pi * freq_distance[transition_mask] / transition_band))
                mask[transition_mask] = transition_values
        else:  # highpass
            # Для ФВЧ создаем плавный подъем около cutoff_freq
            freq_distance = self.cutoff_freq - np.abs(freqs_pos)
            transition_mask = (freq_distance < 0) & (freq_distance > -transition_band)
            if np.any(transition_mask):
                # Косинусное окно для плавного перехода
                transition_values = 0.5 * (1 - np.cos(np.pi * freq_distance[transition_mask] / transition_band))
                mask[transition_mask] = transition_values

        # Применяем маску к спектру
        filtered_fft = signal_fft * mask

        # Обратное преобразование Фурье
        filtered_signal_part = irfft(filtered_fft, n=len(signal_part))

        # Обновляем только указанную часть сигнала
        res_signal.signal_mv[left_idx:right_idx] = filtered_signal_part.tolist()

        return res_signal


# Пример использования
if __name__ == "__main__":
    from CORE.drawer import Drawer
    from CORE.datasets.LUDB import LUDB, LEADS_NAMES
    import matplotlib.pyplot as plt

    # Загружаем тестовый сигнал ЭКГ
    ludb = LUDB()
    patients_ids = ludb.get_patients_ids()
    signal = ludb.get_1d_signal(patient_id=patients_ids[4], lead_name=LEADS_NAMES.i)
    old_signal = signal.get_fragment(0.0, 1)

    # Создаем фильтры
    # ФНЧ - удаляем высокие частоты (оставляем частоты ниже 40 Гц)
    lowpass_filter = FrequencyFilter(cutoff_freq=40.0, filter_type='lowpass')

    # ФВЧ - удаляем низкие частоты (оставляем частоты выше 5 Гц)
    highpass_filter = FrequencyFilter(cutoff_freq=5.0, filter_type='highpass')

    # Применяем фильтры к разным участкам сигнала
    signal_lowpass = lowpass_filter.run(signal=old_signal, left_t=0, right_t=1)
    signal_highpass = highpass_filter.run(signal=old_signal, left_t=0, right_t=1)


    # Визуализация
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

    drawer1 = Drawer(axes[0])
    drawer1.draw_signal(old_signal, name="Исходный сигнал", color='black')
    axes[0].set_title("Исходный сигнал")
    axes[0].grid(True, alpha=0.3)

    drawer2 = Drawer(axes[1])
    drawer2.draw_signal(signal_lowpass, name="ФНЧ", color='blue')
    axes[1].set_title("ФНЧ - удалены высокие частоты")
    axes[1].grid(True, alpha=0.3)

    drawer3 = Drawer(axes[2])
    drawer3.draw_signal(signal_highpass, name="ФВЧ", color='red')
    axes[2].set_title("ФВЧ - удалены низкие частоты")
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
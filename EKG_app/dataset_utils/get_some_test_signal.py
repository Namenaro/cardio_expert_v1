from settings import LEADS_NAMES
from paths import PATH_TO_LUDB

import json
from pathlib import Path

# Чтоб преобразовать x к времени, надо делить на 500.
# Чтоб преобразовать y к mV надо делить на 1000.
# Метод возвращаем не преобразованный сигнал:

def get_some_test_signal():
    # Откроем датасет LUDB
    path_to_dataset = Path(PATH_TO_LUDB)
    with open(path_to_dataset, 'r') as file:
        LUDB_data = json.load(file)

    # возьмем id-шник i-того  пациента датасета
    i = 1
    patient_ids = list(LUDB_data.keys())
    patient_id = patient_ids[i]

    # Выберем интересующее нас отведение
    lead_name = LEADS_NAMES.i

    # вытащим сам сигнал из этого отведения этого пациента
    signal_one_lead_mkV=  LUDB_data[patient_id]['Leads'][lead_name]['Signal']

    return signal_one_lead_mkV


if __name__ == "__main__":
    from visualisation_utils import plot_lead_signal_to_ax
    import matplotlib.pyplot as plt

    signal = get_some_test_signal()

    fig, ax = plt.subplots()
    signal_mV = [s / 1000 for s in signal]  # делим на 1000, т.к. хотим в мВ, а в датасете в мкВ
    plot_lead_signal_to_ax(signal_mV=signal_mV, ax=ax)
    plt.show()

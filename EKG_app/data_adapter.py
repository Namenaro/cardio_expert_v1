from typing import List

from dataset_utils.get_LUDB_data import get_LUDB_data
from dataset_utils.get_signal_by_patient_id import get_signal_by_id_and_lead_mV
from settings import LEADS_NAMES, FREQUENCY

from models import Entry
from core.signal_1d import Signal

class LUDBAdapter:
    """
    Класс-адаптер. Скрывает сложную работу с JSON-словарем
    и предоставляет удобные методы для остального приложения.
    """
    def __init__(self):
        print("Загрузка JSON базы данных в память...")
        self._ludb_data = get_LUDB_data()
        if self._ludb_data:
            print("База данных успешно загружена.")
        else:
            raise IOError("Не удалось загрузить LUDB_data. Проверьте пути.")
    
    def get_all_entries(self) -> List[Entry]:
        """
        Возвращает список всех записей в датасете (только метаданные).
        Сигналы не загружаются для экономии памяти.
        """
        if not self._ludb_data:
            return []

        entries = []
        patient_ids = list(self._ludb_data.keys())
        
        all_leads = LEADS_NAMES.ii
        #all_leads = [LEADS_NAMES.i, LEADS_NAMES.ii, LEADS_NAMES.iii]

        for pid in patient_ids:
            entry = Entry(
                patient_id=pid,
                lead_name=all_leads,
                points={} 
            )
            entries.append(entry)
            
        print(f"Подготовлено {len(entries)} записей для отображения.")
        return entries

    def get_signal_for_entry(self, entry: Entry) -> Signal:
        """
        "Лениво" загружает и возвращает объект Signal для конкретной записи.
        Вызывается только когда пользователь хочет разметить запись.
        """
        signal_mv = get_signal_by_id_and_lead_mV(
            patient_id=entry.patient_id,
            lead_name=entry.lead_name,
            LUDB_data=self._ludb_data
        )
        
        return Signal(signal_mv=signal_mv, frequency=FREQUENCY)
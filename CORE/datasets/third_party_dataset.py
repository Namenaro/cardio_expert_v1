from abc import ABC, abstractmethod
from typing import Optional, List

from CORE.enums import LEADS_NAMES
from CORE.signal_1d import Signal


class ThirdPartyDataset(ABC):
    """
    Базовый класс для датасетов ЭКГ, на которых мы созданем датасеты форм (LUDB, PTB-XL,...)
    """

    @abstractmethod
    def get_1d_signal(self, patient_id: str, lead_name: LEADS_NAMES) -> Optional[Signal]:
        """
            Возвращает одномерный сигнал для указанного пациента и отведения.

            Args:
                patient_id: Идентификатор пациента в файле ecg_data_200.json
                lead_name: Название отведения из LUDB_LEADS_NAMES

            Returns:
                Объект Signal с данными сигнала или None, если сигнал не найден

        """
        pass

    @abstractmethod
    def get_patients_ids(self) -> List[str]:
        """
        Возвращает список id всех записей задасета для последующего использования в get_1d_signal
        Returns: Спискок id пациентов
        """
        pass

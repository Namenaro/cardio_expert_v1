from typing import Dict
from dataclasses import dataclass


@dataclass
class Entry:
    """Одна запись в датасете"""
    entry_id: str  # ID записи
    patient_id: str
    lead_name: str
    points: Dict[str, float]  # Точки как словарь

    @classmethod
    def from_dict(cls, entry_id: str, data: Dict) -> 'Entry':
        """Создание из словаря"""
        return cls(
            entry_id=entry_id,
            patient_id=data.get('patient_id', ''),
            lead_name=data.get('lead_name', ''),
            points=data.get('points', {})
        )

    def validate_points(self, expected_point_names: list) -> bool:
        """Валидация точек (метод есть, но не вызывается)"""
        # Проверяем наличие всех ожидаемых точек
        for point_name in expected_point_names:
            if point_name not in self.points:
                return False
        return True

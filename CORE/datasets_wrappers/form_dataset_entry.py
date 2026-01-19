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


"""
Парсит записи из json такой структуры:
{
  "meta": {
    "points": [
      "p1",
      "p2",
      "p3"
    ]
  },
  "data": {
    "0": {
      "patient_id": "50519553",
      "lead_name": "ii",
      "points": {
        "p1": 0.5308544303797468,
        "p2": 0.5888713080168776,
        "p3": 0.6257911392405063
      }
    },
    "1": {
      "patient_id": "50519553",
      "lead_name": "ii",
      "points": {
        "p1": 1.4322813101310217,
        "p2": 1.4815867394573337,
        "p3": 1.5160430196146473
      }, ........
    }
}
"""

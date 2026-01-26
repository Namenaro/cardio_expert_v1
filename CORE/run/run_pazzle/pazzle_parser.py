from typing import Type, Dict, List

from CORE.db_dataclasses import BasePazzle, ClassInputPoint, ObjectInputPointValue, Point
from CORE.run.run_pazzle.classes_registry import classes_registry


class PazzleParser:
    def __init__(self, base_pazzle: BasePazzle, form_points: List[Point]):
        self.base_pazzle: BasePazzle = base_pazzle
        self.points = form_points

        self.cls: Type = self._get_cls()

    def _get_cls(self) -> Type:
        class_name_str = self.base_pazzle.class_ref.name
        if not isinstance(class_name_str, str) or not class_name_str.strip():
            raise ValueError("Ожидалась непустая строка (без пробелов) в качестве имени класса")
        cls = classes_registry[class_name_str]
        return cls

    def map_point_names(self) -> Dict[str, str]:
        """
        Сопоставляет имя точки в классе (ClassInputPoint.name)
        имени точки в форме (Point.name).

        :return: {имя_точки_в_cls: имя_соотвествующей_точки_в_форме}
        :raises ValueError: если:
            - количество точек не совпадает;
            - есть дублирующиеся имена в ClassInputPoint;
            - нет однозначного соответствия между точками;
            - не найдена точка в форме по point_id.
        """
        points_in_cls: List[ClassInputPoint] = self.base_pazzle.class_ref.input_points
        points_vals: List[ObjectInputPointValue] = self.base_pazzle.input_point_values

        # 1. Проверка: количество точек в сигнатуре класса должно совпадать с полученными из пазла
        if len(points_in_cls) != len(points_vals):
            raise ValueError(f"Количество точек в классе {self.cls} "
                             f"не совпадает c полученными соответствиями "
                             f"из пазла {self.base_pazzle.id}")

        # 2. Проверка уникальности имён в ClassInputPoint
        names = [p.name for p in points_in_cls]
        if len(set(names)) != len(points_in_cls):
            duplicates = [name for name in set(names) if names.count(name) > 1]
            raise ValueError(
                f"Обнаружены дублирующиеся имена точек в сигнатуре "
                f"класса: {sorted(duplicates)}, класс {self.cls}"
            )

        # 3. Словарь точек (из Point.id) по id
        points_by_id: Dict[int, Point] = {
            p.id: p for p in self.points if p.id is not None
        }

        # 4. Сопоставление
        # ClassInputPoint ← input_point_id → ObjectInputPointValue ← point_id → Point
        mapping: Dict[str, str] = {}
        for cls_point in points_in_cls:
            # Ищем все ObjectInputPointValue с input_point_id == cls_point.id
            matches = [
                fp for fp in points_vals
                if fp.input_point_id == cls_point.id
            ]

            # Для данной cls_point должно быть ровно одно соответствие в points_vals
            if len(matches) != 1:
                raise ValueError(f"Точке {cls_point.id} из сигнатуры класса {self.cls} "
                                 f"соответсвует более одного сопоставления в пазле {self.base_pazzle.id}")

            form_point = matches[0]

            # Проверяем, что point_id существует и есть в points_by_id
            if not form_point.point_id or form_point.point_id not in points_by_id:
                raise ValueError("Не найдено соответствующей точки в форме")

            mapping[cls_point.name] = points_by_id[form_point.point_id].name

        return mapping

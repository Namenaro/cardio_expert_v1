from typing import Type, Dict, List, Any, get_type_hints

from CORE.db_dataclasses import BasePazzle, ClassInputPoint, ObjectInputPointValue, Point, Parameter, ClassInputParam, \
    ObjectInputParamValue, ClassOutputParam, ObjectOutputParamValue, ClassArgument, ObjectArgumentValue
from CORE.run.run_pazzle.classes_registry import classes_registry
from CORE.run.run_pazzle.utils import *


class PazzleParser:
    def __init__(self, base_pazzle: BasePazzle, form_points: List[Point], form_params: List[Parameter]):
        self.base_pazzle: BasePazzle = base_pazzle
        self.points = form_points
        self.params = form_params

        self.cls: Type = self._get_cls()

    def _get_cls(self) -> Type:
        class_name_str = self.base_pazzle.class_ref.name
        if not isinstance(class_name_str, str) or not class_name_str.strip():
            raise ValueError("Ожидалась непустая строка в качестве имени класса")
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

    def map_input_params_names(self) -> Dict[str, str]:
        """
        Сопоставляет имя параметра в классе (ClassInputParam.name)
        имени параметра в форме (Parameter.name).

        :return: {имя_параметра_в_cls: имя_соответствующего_параметра_в_форме}
        :raises ValueError: если:
            - количество параметров не совпадает;
            - есть дублирующиеся имена в ClassInputParam;
            - нет однозначного соответствия;
            - не найден параметр в форме по parameter_id.
        """
        params_in_cls: List[ClassInputParam] = self.base_pazzle.class_ref.input_params
        params_vals: List[ObjectInputParamValue] = self.base_pazzle.input_param_values

        # 1. Проверка: количество параметров в сигнатуре класса должно совпадать с полученными из пазла
        if len(params_in_cls) != len(params_vals):
            raise ValueError(f"Количество входных параметров в классе {self.cls} "
                             f"не совпадает с полученными соответствиями "
                             f"из пазла {self.base_pazzle.id}")

        # 2. Проверка уникальности имён в ClassInputParam
        names = [p.name for p in params_in_cls]
        if len(set(names)) != len(params_in_cls):
            duplicates = [name for name in set(names) if names.count(name) > 1]
            raise ValueError(
                f"Обнаружены дублирующиеся имена входных параметров в сигнатуре "
                f"класса: {sorted(duplicates)}, класс {self.cls}"
            )

        # 3. Словарь параметров (из Parameter.id) по id
        params_by_id: Dict[int, Parameter] = {
            p.id: p for p in self.params if p.id is not None
        }

        # 4. Сопоставление
        # ClassInputParam ← input_param_id → ObjectInputParamValue ← parameter_id → Parameter
        mapping: Dict[str, str] = {}
        for cls_param in params_in_cls:
            # Ищем все ObjectInputParamValue с input_param_id == cls_param.id
            matches = [
                pv for pv in params_vals
                if pv.input_param_id == cls_param.id
            ]

            # Для данного cls_param должно быть ровно одно соответствие в params_vals
            if len(matches) != 1:
                raise ValueError(f"Параметру {cls_param.id} из сигнатуры класса {self.cls} "
                                 f"соответствует более одного сопоставления в пазле {self.base_pazzle.id}")

            form_param = matches[0]

            # Проверяем, что parameter_id существует и есть в params_by_id
            if not form_param.parameter_id or form_param.parameter_id not in params_by_id:
                raise ValueError("Не найдено соответствующего параметра в форме")

            mapping[cls_param.name] = params_by_id[form_param.parameter_id].name

        return mapping

    def map_output_params_names(self) -> Dict[str, str]:
        """
        Сопоставляет имя выходного параметра в классе (ClassOutputParam.name)
        имени параметра в форме (Parameter.name).

        :return: {имя_параметра_в_cls: имя_соответствующего_параметра_в_форме}
        :raises ValueError: если:
            - количество выходных параметров не совпадает;
            - есть дублирующиеся имена в ClassOutputParam;
            - нет однозначного соответствия;
            - не найден параметр в форме по parameter_id.
        """
        params_in_cls: List[ClassOutputParam] = self.base_pazzle.class_ref.output_params
        params_vals: List[ObjectOutputParamValue] = self.base_pazzle.output_param_values

        # 1. Проверка: количество выходных параметров в сигнатуре класса должно совпадать с полученными из пазла
        if len(params_in_cls) != len(params_vals):
            raise ValueError(
                f"Количество выходных параметров в классе {self.cls} "
                f"не совпадает с полученными соответствиями "
                f"из пазла {self.base_pazzle.id}"
            )

        # 2. Проверка уникальности имён в ClassOutputParam
        names = [p.name for p in params_in_cls]
        if len(set(names)) != len(params_in_cls):
            duplicates = [name for name in set(names) if names.count(name) > 1]
            raise ValueError(
                f"Обнаружены дублирующиеся имена выходных параметров в сигнатуре "
                f"класса: {sorted(duplicates)}, класс {self.cls}"
            )

        # 3. Словарь параметров (из Parameter.id) по id
        params_by_id: Dict[int, Parameter] = {
            p.id: p for p in self.params if p.id is not None
        }

        # 4. Сопоставление
        # ClassOutputParam ← output_param_id → ObjectOutputParamValue ← parameter_id → Parameter
        mapping: Dict[str, str] = {}
        for cls_param in params_in_cls:
            # Ищем все ObjectOutputParamValue с output_param_id == cls_param.id
            matches = [
                pv for pv in params_vals
                if pv.output_param_id == cls_param.id
            ]

            # Для данного cls_param должно быть ровно одно соответствие в params_vals
            if len(matches) != 1:
                raise ValueError(
                    f"Выходному параметру {cls_param.id} из сигнатуры класса {self.cls} "
                    f"соответствует {len(matches)} сопоставлений в пазле {self.base_pazzle.id}"
                )

            form_param = matches[0]

            # Проверяем, что parameter_id существует и есть в params_by_id
            if not form_param.parameter_id or form_param.parameter_id not in params_by_id:
                raise ValueError(
                    f"Не найдено соответствующего параметра в форме для output_param_id={cls_param.id}, "
                    f"parameter_id={form_param.parameter_id}"
                )

            mapping[cls_param.name] = params_by_id[form_param.parameter_id].name

        return mapping

    def get_constructor_arguments(self) -> Dict[str, Any]:
        """
        Формирует словарь аргументов конструктора класса.

        :return: {имя_аргумента: конвертированное_значение}
        :raises ValueError:
            - если для аргумента нет значения;
            - если для аргумента найдено более одного значения;
            - если тип аргумента не найден в аннотациях;
            - при ошибке конвертации.
        """
        class_args: List[ClassArgument] = self.base_pazzle.class_ref.constructor_arguments
        obj_values: List[ObjectArgumentValue] = self.base_pazzle.argument_values

        # 1. Группируем ObjectArgumentValue по argument_id, отслеживаем дубликаты
        value_by_arg_id: Dict[int, List[ObjectArgumentValue]] = {}
        for val in obj_values:
            if val.argument_id is not None:
                if val.argument_id not in value_by_arg_id:
                    value_by_arg_id[val.argument_id] = []
                value_by_arg_id[val.argument_id].append(val)

        # 2. Получаем аннотации типов из __init__ класса
        try:
            init_hints = get_type_hints(self.cls.__init__)
        except (AttributeError, TypeError) as e:
            raise ValueError(f"Не удалось получить аннотации типов для {self.cls}: {e}")

        result: Dict[str, Any] = {}

        # 3. Обрабатываем каждый аргумент класса
        for arg in class_args:
            arg_name = arg.name
            arg_id = arg.id

            # Проверяем, что аргумент описан в аннотациях конструктора
            if arg_name not in init_hints:
                raise ValueError(
                    f"Тип аргумента '{arg_name}' не найден в аннотации конструктора {self.cls}"
                )

            target_type = init_hints[arg_name]

            # 4. Ищем значения по argument_id
            if arg_id not in value_by_arg_id:
                raise ValueError(f"Нет значения для аргумента '{arg_name}' (id={arg_id})")

            matches = value_by_arg_id[arg_id]

            # 5. Проверяем однозначность соответствия
            if len(matches) > 1:
                raise ValueError(
                    f"Для аргумента '{arg_name}' (id={arg_id}) найдено {len(matches)} значений. "
                    "Ожидается ровно одно соответствие."
                )

            # Берем единственное значение
            raw_value = matches[0].argument_value

            # 6. Конвертируем значение
            try:
                typed_value = convert_value(raw_value, target_type)
            except Exception as e:
                raise ValueError(
                    f"Ошибка конвертации для аргумента '{arg_name}': "
                    f"значение='{raw_value}', тип={target_type}. Ошибка: {e}"
                )

            result[arg_name] = typed_value

        return result

from CORE.db_dataclasses.base_class import BaseClass, CLASS_TYPES
from CORE.db_dataclasses.classes_to_pazzles_helpers import *

import ast
import inspect
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from pathlib import Path


class ClassParser:
    """Парсер для извлечения информации о классах из AST ClassDef"""

    def parse_class(self, class_node: ast.ClassDef) -> BaseClass:
        """Парсит AST класса и возвращает информацию в виде BaseClass"""
        base_class = BaseClass(
            name=class_node.name,
            comment=self._get_class_comment(class_node)
        )

        # Парсим конструктор
        base_class.constructor_arguments = self._parse_constructor(class_node)

        # Парсим метод register_input_parameters
        base_class.input_params = self._parse_register_input_parameters(class_node)

        # Парсим метод register_points
        base_class.input_points = self._parse_register_points(class_node)

        # Парсим выходные параметры
        base_class.output_params = self._parse_output_params(class_node)

        return base_class

    def _get_class_comment(self, class_node: ast.ClassDef) -> str:
        """Извлекает комментарий к классу"""
        if not class_node.body:
            return ""

        first_element = class_node.body[0]
        match first_element:
            case ast.Expr(value=ast.Constant(value=str() as comment)):
                return comment.strip()
            case ast.Expr(value=ast.Str(s=comment)):
                return comment.strip()

        return ""

    def _parse_constructor(self, class_node: ast.ClassDef) -> List[ClassArgument]:
        """Парсит конструктор класса (метод __init__)"""
        constructor_args = []

        init_method = self._find_method(class_node, "__init__")
        if not init_method:
            return constructor_args

        # Пропускаем self
        args = init_method.args.args[1:] if init_method.args.args else []
        defaults = init_method.args.defaults

        # Собираем информацию о параметрах
        for i, arg in enumerate(args):
            param_name = arg.arg

            # Получаем тип данных и нормализуем его
            raw_data_type = ast.unparse(arg.annotation) if arg.annotation else ""
            data_type = self._normalize_data_type(raw_data_type)

            # Получаем значение по умолчанию
            default_value = None
            default_start_index = len(args) - len(defaults)
            if i >= default_start_index:
                default_index = i - default_start_index
                default_value_str = ast.unparse(defaults[default_index])
                if default_value_str:
                    default_value = default_value_str

            # Получаем комментарий к параметру
            comment = self._get_param_comment(init_method, param_name)

            constructor_args.append(ClassArgument(
                name=param_name,
                comment=comment,
                data_type=data_type,
                default_value=default_value
            ))

        return constructor_args

    def _parse_register_points(self, class_node: ast.ClassDef) -> List[ClassInputPoint]:
        """Парсит метод register_points"""
        input_points = []

        method = self._find_method(class_node, "register_points")
        if not method:
            return input_points

        # Пропускаем self
        args = method.args.args[1:] if method.args.args else []

        for arg in args:
            param_name = arg.arg
            comment = self._get_param_comment(method, param_name)

            input_points.append(ClassInputPoint(
                name=param_name,
                comment=comment
            ))

        return input_points

    def _parse_register_input_parameters(self, class_node: ast.ClassDef) -> List[ClassInputParam]:
        """Парсит метод register_input_parameters"""
        input_params = []

        method = self._find_method(class_node, "register_input_parameters")
        if not method:
            return input_params

        # Пропускаем self
        args = method.args.args[1:] if method.args.args else []

        for arg in args:
            param_name = arg.arg
            raw_data_type = ast.unparse(arg.annotation) if arg.annotation else ""
            data_type = self._normalize_data_type(raw_data_type)
            comment = self._get_param_comment(method, param_name)

            input_params.append(ClassInputParam(
                name=param_name,
                comment=comment,
                data_type=data_type
            ))

        return input_params

    def _parse_output_params(self, class_node: ast.ClassDef) -> list[ClassOutputParam]:
        """Парсит OUTPUT_SCHEMA из класса (Python 3.13+)"""
        for item in class_node.body:
            match item:
                case ast.Assign(
                    targets=[ast.Name(id="OUTPUT_SCHEMA")],
                    value=ast.Dict(keys=keys, values=values)
                ):
                    output_params = []
                    for key, value in zip(keys, values):
                        match (key, value):
                            case (ast.Constant(value=param_name),
                                  ast.Tuple(elts=[type_node, ast.Constant(value=description)])):

                                # Извлекаем тип
                                match type_node:
                                    case ast.Name(id=type_name):
                                        data_type = type_name
                                    case _:
                                        data_type = ast.unparse(type_node)

                                output_params.append(ClassOutputParam(
                                    name=param_name,
                                    data_type=data_type,
                                    comment=description
                                ))
                    return output_params

        return []

    def _normalize_data_type(self, data_type: str) -> str:
        """Нормализует тип данных к значениям из DATA_TYPES"""
        if not data_type:
            return ""

        # Приводим к нижнему регистру для сравнения
        data_type_lower = data_type.lower().strip()

        # Проверяем соответствие с типами из DATA_TYPES
        for enum_member in DATA_TYPES:
            if enum_member.value == data_type_lower:
                return enum_member.value

        # Если тип не найден в DATA_TYPES, возвращаем исходный
        return data_type_lower

    def _find_method(self, class_node: ast.ClassDef, method_name: str) -> Optional[ast.FunctionDef]:
        """Находит метод в классе по имени"""
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                return node
        return None

    def _find_inner_class(self, class_node: ast.ClassDef, inner_class_name: str) -> Optional[ast.ClassDef]:
        """Находит внутренний класс по имени"""
        for node in class_node.body:
            if isinstance(node, ast.ClassDef) and node.name == inner_class_name:
                return node
        return None

    def _is_dataclass(self, class_node: ast.ClassDef) -> bool:
        """Проверяет, является ли класс dataclass"""
        for decorator in class_node.decorator_list:
            match decorator:
                case ast.Name(id='dataclass'):
                    return True
                case ast.Attribute(value=ast.Name(id='dataclasses'), attr='dataclass'):
                    return True
                case ast.Call(func=ast.Name(id='dataclass')):
                    return True
        return False

    def _get_param_comment(self, function_node: ast.FunctionDef, param_name: str) -> str:
        """Извлекает комментарий к параметру из docstring"""
        docstring = ast.get_docstring(function_node)
        if not docstring:
            return ""

        lines = docstring.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()

            # Ищем стандартные форматы документации
            if f":param {param_name}:" in line or f":arg {param_name}:" in line:
                # Извлекаем комментарий из той же строки
                parts = line.split(":", 2)
                if len(parts) > 2:
                    comment = parts[2].strip()
                    if comment:
                        return comment

                # Или ищем на следующей строке
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line and not next_line.startswith(":"):
                        return next_line

            # Альтернативный формат: param_name - описание
            if line.startswith(param_name + " ") or line.startswith(param_name + ":"):
                parts = line.split(" ", 1)
                if len(parts) > 1:
                    return parts[1].strip()

        return ""

    def _get_field_comment(self, assign_node: ast.AnnAssign) -> str:
        """Извлекает комментарии к полю dataclass всеми способами"""
        comments = []

        try:
            # Способ 1: Строковые литералы вокруг поля
            comments.extend(self._get_string_literals_comment(assign_node))

            # Способ 2: Field с metadata
            comments.extend(self._get_field_metadata_comment(assign_node))

            # Способ 3: Inline комментарии (через #)
            comments.extend(self._get_inline_comment(assign_node))

        except Exception:
            pass

        return " | ".join(comments) if comments else ""

    def _get_string_literals_comment(self, assign_node: ast.AnnAssign) -> List[str]:
        """Извлекает комментарии из строковых литералов вокруг поля"""
        comments = []

        try:
            if not hasattr(assign_node, 'parent') or not assign_node.parent:
                return comments

            parent_body = getattr(assign_node.parent, 'body', [])
            if not parent_body:
                return comments

            field_index = -1
            for i, node in enumerate(parent_body):
                if node is assign_node:
                    field_index = i
                    break

            if field_index == -1:
                return comments

            # Ищем строковые литералы ПЕРЕД полем
            for i in range(field_index - 1, -1, -1):
                prev_node = parent_body[i]
                if isinstance(prev_node, ast.AnnAssign):
                    break
                comment = self._extract_string_from_node(prev_node)
                if comment:
                    comments.insert(0, comment)
                else:
                    break

            # Ищем строковые литералы ПОСЛЕ поля
            for i in range(field_index + 1, len(parent_body)):
                next_node = parent_body[i]
                if isinstance(next_node, ast.AnnAssign):
                    break
                comment = self._extract_string_from_node(next_node)
                if comment:
                    comments.append(comment)
                else:
                    break

        except Exception:
            pass

        return comments

    def _get_field_metadata_comment(self, assign_node: ast.AnnAssign) -> List[str]:
        """Извлекает комментарий из field(metadata=...)"""
        comments = []

        try:
            # Проверяем, есть ли значение с field()
            if (hasattr(assign_node, 'value') and
                    isinstance(assign_node.value, ast.Call) and
                    isinstance(assign_node.value.func, ast.Name) and
                    assign_node.value.func.id == 'field'):

                # Ищем аргумент metadata
                for keyword in assign_node.value.keywords:
                    if keyword.arg == 'metadata' and isinstance(keyword.value, ast.Dict):
                        # Ищем description в metadata
                        keys = keyword.value.keys
                        values = keyword.value.values
                        for k, v in zip(keys, values):
                            if (isinstance(k, ast.Constant) and k.value == 'description' and
                                    isinstance(v, ast.Constant) and isinstance(v.value, str)):
                                comments.append(v.value)

        except Exception:
            pass

        return comments

    def _get_inline_comment(self, assign_node: ast.AnnAssign) -> List[str]:
        """Извлекает inline комментарии (через #) - требует доступа к исходному коду"""
        # Этот способ сложнее, так как требует исходного кода
        # Вам нужно будет передавать исходный код в парсер
        return []

    def _extract_string_from_node(self, node) -> str:
        """Извлекает строку из AST узла"""
        try:
            if isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                    return node.value.value.strip()
                elif hasattr(node.value, 's') and isinstance(node.value.s, str):
                    return node.value.s.strip()
        except Exception:
            pass
        return ""

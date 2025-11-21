from CORE.db_dataclasses import *

import logging
from typing import List, Optional


class ParameterService:
    """
    Сервис для управления параметрами (parameter) в формах.
    Обеспечивает операции создания, обновления и мягкого удаления параметров
    с поддержанием целостности базы данных через установку NULL в связанных таблицах.
    Параметры не удаляются физически из базы, а заменяются на NULL в связях.
    """

    def add_parameter(self, conn, parameter: Parameter, form_id: int) -> Parameter:
        """
        Добавляет новый параметр в базу данных.

        Args:
            conn: Соединение с базой данных
            parameter: Объект параметра для добавления
            form_id: ID формы, к которой привязан параметр

        Returns:
            Объект Parameter с заполненным ID
        """
        cursor = conn.cursor()

        # Добавляем параметр
        cursor.execute('''
            INSERT INTO parameter (name, form_id, comment, data_type)
            VALUES (?, ?, ?, ?)
        ''', (parameter.name, form_id, parameter.comment, parameter.data_type))

        parameter_id = cursor.lastrowid
        parameter.id = parameter_id

        logging.info(f"Параметр {parameter_id} успешно добавлен к форме {form_id}")
        return parameter

    def update_parameter(self, conn, parameter: Parameter) -> Parameter:
        """
        Обновляет параметр в базе данных.

        Args:
            conn: Соединение с базой данных
            parameter: Объект параметра с обновленными данными

        Returns:
            Обновленный объект Parameter
        """
        if not parameter.id:
            raise ValueError("Parameter ID is required for update")

        cursor = conn.cursor()

        # Проверяем существование параметра
        cursor.execute("SELECT id FROM parameter WHERE id = ?", (parameter.id,))
        if not cursor.fetchone():
            raise ValueError(f"Parameter with ID {parameter.id} not found")

        # Обновляем параметр
        cursor.execute('''
            UPDATE parameter 
            SET name = ?, comment = ?, data_type = ?
            WHERE id = ?
        ''', (parameter.name, parameter.comment, parameter.data_type, parameter.id))

        logging.info(f"Параметр {parameter.id} успешно обновлен")
        return parameter

    def delete_parameter(self, conn, parameter_id: int) -> bool:
        """
        Мягко удаляет параметр, устанавливая NULL во всех связанных таблицах.

        Args:
            conn: Соединение с базой данных
            parameter_id: ID параметра для удаления

        Returns:
            True если удаление успешно, False если параметр не найден
        """
        cursor = conn.cursor()

        # Проверяем существование параметра
        cursor.execute("SELECT id FROM parameter WHERE id = ?", (parameter_id,))
        if not cursor.fetchone():
            return False

        # Устанавливаем NULL во всех связанных таблицах в правильном порядке

        # 1. Таблица value_to_input_param - parameter_id
        cursor.execute('''
            UPDATE value_to_input_param 
            SET parameter_id = NULL 
            WHERE parameter_id = ?
        ''', (parameter_id,))

        # 2. Таблица value_to_output_param - parameter_id
        cursor.execute('''
            UPDATE value_to_output_param 
            SET parameter_id = NULL 
            WHERE parameter_id = ?
        ''', (parameter_id,))

        # 3. Удаляем сам параметр
        cursor.execute("DELETE FROM parameter WHERE id = ?", (parameter_id,))

        logging.info(f"Параметр {parameter_id} успешно удален, все связи установлены в NULL")
        return True

    def get_parameter_by_id(self, conn, parameter_id: int) -> Optional[Parameter]:
        """
        Получает параметр по ID.

        Args:
            conn: Соединение с базой данных
            parameter_id: ID параметра

        Returns:
            Объект Parameter или None если не найден
        """
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM parameter WHERE id = ?", (parameter_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return Parameter(
            id=row['id'],
            name=row['name'],
            comment=row['comment'],
            data_type=row['data_type']
        )

    def get_parameters_by_form(self, conn, form_id: int) -> List[Parameter]:
        """
        Получает все параметры формы.

        Args:
            conn: Соединение с базой данных
            form_id: ID формы

        Returns:
            Список параметров формы
        """
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM parameter WHERE form_id = ?", (form_id,))
        rows = cursor.fetchall()

        parameters = []
        for row in rows:
            parameters.append(Parameter(
                id=row['id'],
                name=row['name'],
                comment=row['comment'],
                data_type=row['data_type']
            ))

        return parameters

    def is_parameter_used(self, conn, parameter_id: int) -> bool:
        """
        Проверяет, используется ли параметр в каких-либо связях.

        Args:
            conn: Соединение с базой данных
            parameter_id: ID параметра

        Returns:
            True если параметр используется, False если нет
        """
        cursor = conn.cursor()

        # Проверяем использование в таблице value_to_input_param
        cursor.execute('''
            SELECT COUNT(*) as count FROM value_to_input_param 
            WHERE parameter_id = ?
        ''', (parameter_id,))
        input_param_count = cursor.fetchone()['count']

        # Проверяем использование в таблице value_to_output_param
        cursor.execute('''
            SELECT COUNT(*) as count FROM value_to_output_param 
            WHERE parameter_id = ?
        ''', (parameter_id,))
        output_param_count = cursor.fetchone()['count']

        return (input_param_count > 0) or (output_param_count > 0)
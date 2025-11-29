from CORE.db_dataclasses import *

import logging
from typing import List, Optional

class PointService:
    """
    Сервис для управления точками (point) в формах.
    Обеспечивает операции создания, обновления и мягкого удаления точек
    с поддержанием целостности базы данных через установку NULL в связанных таблицах.
    Точки не удаляются физически из базы, а заменяются на NULL в связях.
    """

    def add_point(self, conn, point: Point, form_id: int) -> Point:
        """
        Добавляет новую точку в базу данных.

        Args:
            conn: Соединение с базой данных
            point: Объект точки для добавления
            form_id: ID формы, к которой привязана точка

        Returns:
            Объект Point с заполненным ID
        """
        cursor = conn.cursor()

        # Добавляем точку
        cursor.execute('''
            INSERT INTO point (name, comment, form_id)
            VALUES (?, ?, ?)
        ''', (point.name, point.comment, form_id))

        point_id = cursor.lastrowid
        point.id = point_id

        logging.info(f"Точка {point_id} успешно добавлена к форме {form_id}")
        return point

    def update_point(self, conn, point: Point) -> Point:
        """
        Обновляет точку в базе данных.

        Args:
            conn: Соединение с базой данных
            point: Объект точки с обновленными данными

        Returns:
            Обновленный объект Point
        """
        if not point.id:
            raise ValueError("Point ID is required for update")

        cursor = conn.cursor()

        # Проверяем существование точки
        cursor.execute("SELECT id FROM point WHERE id = ?", (point.id,))
        if not cursor.fetchone():
            raise ValueError(f"Point with ID {point.id} not found")

        # Обновляем точку
        cursor.execute('''
            UPDATE point 
            SET name = ?, comment = ?
            WHERE id = ?
        ''', (point.name, point.comment, point.id))

        logging.info(f"Точка {point.id} успешно обновлена")
        return point

    def delete_point(self, conn, point_id: int) -> bool:
        """
        Мягко удаляет точку, устанавливая NULL во всех связанных таблицах.

        Args:
            conn: Соединение с базой данных
            point_id: ID точки для удаления

        Returns:
            True если удаление успешно, False если точка не найдена
        """
        cursor = conn.cursor()

        # Проверяем существование точки
        cursor.execute("SELECT id FROM point WHERE id = ?", (point_id,))
        if not cursor.fetchone():
            return False

        # Устанавливаем NULL во всех связанных таблицах в правильном порядке

        # 1. Таблица step - target_point_id
        cursor.execute('''
            UPDATE step 
            SET target_point_id = NULL 
            WHERE target_point_id = ?
        ''', (point_id,))

        # 2. Таблица step - left_point_id
        cursor.execute('''
            UPDATE step 
            SET left_point_id = NULL 
            WHERE left_point_id = ?
        ''', (point_id,))

        # 3. Таблица step - right_point_id
        cursor.execute('''
            UPDATE step 
            SET right_point_id = NULL 
            WHERE right_point_id = ?
        ''', (point_id,))

        # 4. Таблица value_to_input_point - point_id
        cursor.execute('''
            UPDATE value_to_input_point 
            SET point_id = NULL 
            WHERE point_id = ?
        ''', (point_id,))

        # 5. Удаляем саму точку
        cursor.execute("DELETE FROM point WHERE id = ?", (point_id,))

        logging.info(f"Точка {point_id} успешно удалена, все связи установлены в NULL")
        return True

    def get_point_by_id(self, conn, point_id: int) -> Optional[Point]:
        """
        Получает точку по ID.

        Args:
            conn: Соединение с базой данных
            point_id: ID точки

        Returns:
            Объект Point или None если не найден
        """
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM point WHERE id = ?", (point_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return Point(
            id=row['id'],
            name=row['name'],
            comment=row['comment']
        )

    def get_points_by_form(self, conn, form_id: int) -> List[Point]:
        """
        Получает все точки формы.

        Args:
            conn: Соединение с базой данных
            form_id: ID формы

        Returns:
            Список точек формы
        """
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM point WHERE form_id = ?", (form_id,))
        rows = cursor.fetchall()

        points = []
        for row in rows:
            points.append(Point(
                id=row['id'],
                name=row['name'],
                comment=row['comment']
            ))

        return points

    def is_point_used(self, conn, point_id: int) -> bool:
        """
        Проверяет, используется ли точка в каких-либо связях.

        Args:
            conn: Соединение с базой данных
            point_id: ID точки

        Returns:
            True если точка используется, False если нет
        """
        cursor = conn.cursor()

        # Проверяем использование в таблице step
        cursor.execute('''
            SELECT COUNT(*) as count FROM step 
            WHERE target_point_id = ? OR left_point_id = ? OR right_point_id = ?
        ''', (point_id, point_id, point_id))
        step_count = cursor.fetchone()['count']

        # Проверяем использование в таблице value_to_input_point
        cursor.execute('''
            SELECT COUNT(*) as count FROM value_to_input_point 
            WHERE point_id = ?
        ''', (point_id,))
        input_point_count = cursor.fetchone()['count']

        return (step_count > 0) or (input_point_count > 0)
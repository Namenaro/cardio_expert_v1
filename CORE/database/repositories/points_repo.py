from CORE.db_dataclasses import Form, Track, Point, Parameter
from CORE.database.db_manager import DBManager

import sqlite3
from typing import List, Optional, Dict


class PointsRepo:

    def add_new_point(self, conn: sqlite3.Connection, form_id: int, point: Point) -> int:
        """
        Добавляет новую точку для указанной формы
        Возвращает ID созданной точки
        """

        cursor = conn.cursor()
        cursor.execute('''
                INSERT INTO point (name, comment, form_id)
                VALUES (?, ?, ?)
        ''', (point.name, point.comment, form_id))

        point_id = cursor.lastrowid
        conn.commit()
        return point_id


    def delete_point_by_id(self, conn: sqlite3.Connection, point_id: int) -> bool:
        """
        Удаляет точку по её ID
        Возвращает True если удаление успешно
        """

        cursor = conn.cursor()
        cursor.execute('DELETE FROM point WHERE id = ?', (point_id,))
        conn.commit()
        return cursor.rowcount > 0


    def read_all_points_by_form_id(self, conn: sqlite3.Connection, form_id: int) -> List[Point]:
        """
        Возвращает список всех точек для указанной формы
        """

        cursor = conn.cursor()
        cursor.execute('''
                SELECT id, name, comment 
                FROM point 
                WHERE form_id = ?
                ORDER BY id
            ''', (form_id,))

        points = []
        for row in cursor.fetchall():
            point = Point(
                    id=row[0],
                    name=row[1],
                    comment=row[2]
            )
            points.append(point)

        return points


    def update_point(self, conn: sqlite3.Connection, point: Point) -> bool:
        """
        Обновляет данные точки
        Возвращает True если обновление успешно, False в случае ошибки
        """
        if point.id is None:
            print("Ошибка: ID точки не указан")
            return False


        cursor = conn.cursor()
        cursor.execute('''
            UPDATE point 
            SET name = ?, comment = ?
            WHERE id = ?
        ''', (point.name, point.comment, point.id))

        conn.commit()
        return cursor.rowcount > 0


    def delete_all_points_of_form(self, conn: sqlite3.Connection, form_id: int) -> bool:
        """
        Удаляет все точки указанной формы
        Возвращает True если удаление успешно, False в случае ошибки
        """

        cursor = conn.cursor()
        cursor.execute('DELETE FROM point WHERE form_id = ?', (form_id,))
        conn.commit()
        return cursor.rowcount > 0




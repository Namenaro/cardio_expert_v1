from CORE.db_dataclasses import Form, Track, Point,  Parameter, BaseClass, BasePazzle, Step, Track, CLASS_TYPES, DATA_TYPES
from CORE.database.db_manager import DBManager
from CORE.database.repositories import *
from CORE.database.repositories.objects_helpers_repos import *
from CORE.database.repositories.objects_helpers_repos.base_repo import BaseRepo


import sqlite3

from typing import List, Optional, Dict
import logging

class StepsRepo(BaseRepo):
    """Репозиторий для работы с шагами, треками и их связями"""

    # Методы для работы с шагами (step)
    def add_step(self, conn: sqlite3.Connection, form_id: int, target_point_id: int,
                 left_point_id: Optional[int], right_point_id: Optional[int],
                 left_padding: Optional[float], right_padding: Optional[float],
                 comment: str, num_in_form: int) -> Optional[int]:
        """Добавляет шаг к форме"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO step (form_id, target_point_id, left_point_id, right_point_id,
                                left_padding, right_padding, comment, num_in_form)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (form_id, target_point_id, left_point_id, right_point_id,
                  left_padding, right_padding, comment, num_in_form))

            step_id = cursor.lastrowid
            conn.commit()
            return step_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении шага: {e}")
            conn.rollback()
            return None

    def get_steps_by_form(self, conn: sqlite3.Connection, form_id: int) -> List[Step]:
        """Получает все шаги формы"""
        rows = self._execute_fetchall(conn,
                                      '''SELECT id, form_id, target_point_id, left_point_id, right_point_id,
                                                left_padding, right_padding, comment, num_in_form
                                         FROM step 
                                         WHERE form_id = ? 
                                         ORDER BY num_in_form''',
                                      (form_id,))

        steps = []
        for row in rows:
            step = Step(
                id=row['id'],
                comment=row['comment'],
                left_padding_t=row['left_padding'],
                right_padding_t=row['right_padding']
            )
            steps.append(step)

        return steps

    def update_step(self, conn: sqlite3.Connection, step: Step) -> bool:
        """Обновляет шаг"""
        if step.id is None:
            print("Ошибка: ID шага не указан")
            return False

        return self._execute_commit(conn,
                                    '''UPDATE step 
                                       SET left_point_id = ?, right_point_id = ?, left_padding = ?, 
                                           right_padding = ?, comment = ?, num_in_form = ?
                                       WHERE id = ?''',
                                    (step.left_point.id if step.left_point else None,
                                     step.right_point.id if step.right_point else None,
                                     step.left_padding_t, step.right_padding_t,
                                     step.comment, step.num_in_form, step.id))

    def delete_step(self, conn: sqlite3.Connection, step_id: int) -> bool:
        """Удаляет шаг по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM step WHERE id = ?',
                                    (step_id,))

    def delete_all_steps_of_form(self, conn: sqlite3.Connection, form_id: int) -> bool:
        """Удаляет все шаги формы"""
        return self._execute_commit(conn,
                                    'DELETE FROM step WHERE form_id = ?',
                                    (form_id,))

    # Методы для работы с треками (track)
    def add_track(self, conn: sqlite3.Connection, step_id: int) -> Optional[int]:
        """Добавляет трек к шагу"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO track (step_id)
                VALUES (?)
            ''', (step_id,))

            track_id = cursor.lastrowid
            conn.commit()
            return track_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении трека: {e}")
            conn.rollback()
            return None

    def get_tracks_by_step(self, conn: sqlite3.Connection, step_id: int) -> List[Track]:
        """Получает все треки шага"""
        rows = self._execute_fetchall(conn,
                                      'SELECT id FROM track WHERE step_id = ? ORDER BY id',
                                      (step_id,))

        tracks = []
        for row in rows:
            track = Track(id=row['id'])
            tracks.append(track)

        return tracks

    def delete_track(self, conn: sqlite3.Connection, track_id: int) -> bool:
        """Удаляет трек по ID"""
        return self._execute_commit(conn,
                                    'DELETE FROM track WHERE id = ?',
                                    (track_id,))

    def delete_all_tracks_of_step(self, conn: sqlite3.Connection, step_id: int) -> bool:
        """Удаляет все треки шага"""
        return self._execute_commit(conn,
                                    'DELETE FROM track WHERE step_id = ?',
                                    (step_id,))

    # Методы для работы со связями объектов и треков (object_to_track)
    def add_object_to_track(self, conn: sqlite3.Connection, track_id: int, object_id: int, num_in_track: int) -> Optional[int]:
        """Добавляет объект к треку"""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO object_to_track (track_id, object_id, num_in_track)
                VALUES (?, ?, ?)
            ''', (track_id, object_id, num_in_track))

            relation_id = cursor.lastrowid
            conn.commit()
            return relation_id
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении объекта к треку: {e}")
            conn.rollback()
            return None

    def get_objects_by_track(self, conn: sqlite3.Connection, track_id: int) -> List[int]:
        """Получает список ID объектов в треке"""
        rows = self._execute_fetchall(conn,
                                      'SELECT object_id FROM object_to_track WHERE track_id = ? ORDER BY num_in_track',
                                      (track_id,))

        return [row['object_id'] for row in rows]

    def delete_object_from_track(self, conn: sqlite3.Connection, track_id: int, object_id: int) -> bool:
        """Удаляет объект из трека"""
        return self._execute_commit(conn,
                                    'DELETE FROM object_to_track WHERE track_id = ? AND object_id = ?',
                                    (track_id, object_id))

    def delete_all_objects_from_track(self, conn: sqlite3.Connection, track_id: int) -> bool:
        """Удаляет все объекты из трека"""
        return self._execute_commit(conn,
                                    'DELETE FROM object_to_track WHERE track_id = ?',
                                    (track_id,))

    def delete_all_objects_from_step(self, conn: sqlite3.Connection, step_id: int) -> bool:
        """Удаляет все объекты из всех треков шага"""
        # Сначала получаем все треки шага
        tracks = self.get_tracks_by_step(conn, step_id)
        for track in tracks:
            if track.id:
                self.delete_all_objects_from_track(conn, track.id)
        return True
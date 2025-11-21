from CORE.db.forms_services.track_service import TrackService
from CORE.db_dataclasses import Step, Point

import logging
from typing import Optional


class StepService:
    """
    Сервис для управления шагами (step) и их связями с треками и точками.
    Обеспечивает каскадные операции с шагами, включая управление треками через TrackService.
    Поддерживает полное жизненное управление шагами с сохранением целостности данных.
    Точки (point) не создаются и не удаляются этим сервисом - они считаются существующими.
    """

    def __init__(self):
        """
        Инициализация сервиса шагов.

        Args:
            track_service: Сервис для работы с треками
        """
        self.track_service = TrackService()

    def delete_step(self, conn, step_id: int) -> bool:
        """
        Каскадно удаляет шаг и все связанные с ним треки и их объекты.

        Args:
            conn: Соединение с базой данных
            step_id: ID шага для удаления

        Returns:
            True если удаление успешно, False если шаг не найден
        """
        cursor = conn.cursor()

        # Проверяем существование шага
        cursor.execute("SELECT id FROM step WHERE id = ?", (step_id,))
        if not cursor.fetchone():
            return False

        # Получаем все треки шага для каскадного удаления
        cursor.execute("SELECT id FROM track WHERE step_id = ?", (step_id,))
        track_ids = [row['id'] for row in cursor.fetchall()]

        # Удаляем треки через track_service
        for track_id in track_ids:
            self.track_service.delete_track(conn, track_id)

        # Удаляем сам шаг
        cursor.execute("DELETE FROM step WHERE id = ?", (step_id,))

        logging.info(f"Шаг {step_id} и все связанные треки успешно удалены")
        return True

    def add_step(self, conn, step: Step, form_id: int) -> Step:
        """
        Добавляет новый шаг в базу данных.

        Args:
            conn: Соединение с базой данных
            step: Объект шага для добавления
            form_id: ID формы, к которой привязан шаг

        Returns:
            Объект Step с заполненным ID и ID треков
        """
        cursor = conn.cursor()

        # Валидация точек (должны существовать в базе)
        if not step.target_point or not step.target_point.id:
            raise ValueError("Target point must have ID")
        if step.left_point and not step.left_point.id:
            raise ValueError("Left point must have ID if provided")
        if step.right_point and not step.right_point.id:
            raise ValueError("Right point must have ID if provided")

        # Добавляем основной шаг
        cursor.execute('''
            INSERT INTO step (form_id, target_point_id, left_point_id, right_point_id, 
                            left_padding, right_padding, comment, num_in_form)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            form_id,
            step.target_point.id,
            step.left_point.id if step.left_point else None,
            step.right_point.id if step.right_point else None,
            step.left_padding_t,
            step.right_padding_t,
            step.comment,
            step.num_in_form
        ))

        step_id = cursor.lastrowid
        step.id = step_id

        # Добавляем треки шага через track_service
        self._add_step_tracks(conn, step_id, step)

        # Получаем полный шаг с заполненными ID треков
        result = self.get_step_by_id(conn, step_id)
        logging.info(f"Шаг {step_id} успешно добавлен")
        return result

    def update_step(self, conn, step: Step) -> Step:
        """
        Обновляет шаг и его треки.

        Args:
            conn: Соединение с базой данных
            step: Объект шага с обновленными данными

        Returns:
            Обновленный объект Step
        """
        if not step.id:
            raise ValueError("Step ID is required for update")

        cursor = conn.cursor()

        # Проверяем существование шага
        cursor.execute("SELECT id FROM step WHERE id = ?", (step.id,))
        if not cursor.fetchone():
            raise ValueError(f"Step with ID {step.id} not found")

        # Получаем текущую версию шага
        current_step = self.get_step_by_id(conn, step.id)
        if not current_step:
            raise ValueError(f"Step with ID {step.id} not found")

        # Валидация точек (должны существовать в базе)
        if not step.target_point or not step.target_point.id:
            raise ValueError("Target point must have ID")
        if step.left_point and not step.left_point.id:
            raise ValueError("Left point must have ID if provided")
        if step.right_point and not step.right_point.id:
            raise ValueError("Right point must have ID if provided")

        # Обновляем основные данные шага
        cursor.execute('''
            UPDATE step 
            SET target_point_id = ?, left_point_id = ?, right_point_id = ?,
                left_padding = ?, right_padding = ?, comment = ?, num_in_form = ?
            WHERE id = ?
        ''', (
            step.target_point.id,
            step.left_point.id if step.left_point else None,
            step.right_point.id if step.right_point else None,
            step.left_padding_t,
            step.right_padding_t,
            step.comment,
            step.num_in_form,
            step.id
        ))

        # Обновляем треки шага
        self._update_step_tracks(conn, step.id, step, current_step)

        # Получаем обновленный шаг
        result = self.get_step_by_id(conn, step.id)
        logging.info(f"Шаг {step.id} успешно обновлен")
        return result

    def get_step_by_id(self, conn, step_id: int) -> Optional[Step]:
        """
        Получает шаг по ID со всеми связанными треками.
        """
        cursor = conn.cursor()

        # Получаем основную информацию о шаге
        cursor.execute('''
            SELECT s.*, 
                   tp.id as target_point_id, tp.name as target_point_name, tp.comment as target_point_comment,
                   lp.id as left_point_id, lp.name as left_point_name, lp.comment as left_point_comment,
                   rp.id as right_point_id, rp.name as right_point_name, rp.comment as right_point_comment
            FROM step s
            LEFT JOIN point tp ON s.target_point_id = tp.id
            LEFT JOIN point lp ON s.left_point_id = lp.id
            LEFT JOIN point rp ON s.right_point_id = rp.id
            WHERE s.id = ?
        ''', (step_id,))

        step_row = cursor.fetchone()

        if not step_row:
            return None

        # Создаем объекты точек (обрабатываем NULL)
        target_point = None
        if step_row['target_point_id']:
            target_point = Point(
                id=step_row['target_point_id'],
                name=step_row['target_point_name'] or "",
                comment=step_row['target_point_comment'] or ""
            )

        left_point = None
        if step_row['left_point_id']:
            left_point = Point(
                id=step_row['left_point_id'],
                name=step_row['left_point_name'] or "",
                comment=step_row['left_point_comment'] or ""
            )

        right_point = None
        if step_row['right_point_id']:
            right_point = Point(
                id=step_row['right_point_id'],
                name=step_row['right_point_name'] or "",
                comment=step_row['right_point_comment'] or ""
            )

        # Создаем объект шага
        step = Step(
            id=step_row['id'],
            num_in_form=step_row['num_in_form'],
            target_point=target_point,
            left_point=left_point,
            right_point=right_point,
            left_padding_t=step_row['left_padding'],
            right_padding_t=step_row['right_padding'],
            comment=step_row['comment'] or ""
        )

        # Загружаем треки шага
        cursor.execute("SELECT id FROM track WHERE step_id = ?", (step_id,))
        track_ids = [row['id'] for row in cursor.fetchall()]

        for track_id in track_ids:
            track = self.track_service.get_track_by_id(conn, track_id)
            if track:
                step.tracks.append(track)

        return step

    def _add_step_tracks(self, conn, step_id: int, step: Step):
        """
        Добавляет треки шага.

        Args:
            conn: Соединение с базой данных
            step_id: ID шага
            step: Объект шага с треками
        """
        for track in step.tracks:
            self.track_service.add_track(conn, track, step_id)

    def _update_step_tracks(self, conn, step_id: int, new_step: Step, current_step: Step):
        """
        Обновляет треки шага.

        Args:
            conn: Соединение с базой данных
            step_id: ID шага
            new_step: Новый объект шага
            current_step: Текущий объект шага из БД
        """
        # Создаем словари для быстрого поиска текущих треков
        current_tracks = {track.id: track for track in current_step.tracks if track.id}

        # Обновляем существующие треки и добавляем новые
        new_track_ids = set()
        for new_track in new_step.tracks:
            if new_track.id and new_track.id in current_tracks:
                # Обновляем существующий трек
                updated_track = self.track_service.update_track(conn, new_track)
                new_track = updated_track
            else:
                # Добавляем новый трек
                added_track = self.track_service.add_track(conn, new_track, step_id)
                new_track = added_track
            if new_track.id:
                new_track_ids.add(new_track.id)

        # Удаляем треки, которых больше нет в шаге
        current_track_ids = set(current_tracks.keys())
        deleted_track_ids = current_track_ids - new_track_ids

        for track_id in deleted_track_ids:
            self.track_service.delete_track(conn, track_id)
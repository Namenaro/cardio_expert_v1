from CORE.db.forms_services.objects_service import ObjectsService
from CORE.db_dataclasses import *

import logging
from typing import Optional


class TrackService:
    """
    Сервис для управления треками (track) и их связями с объектами.
    Обеспечивает каскадные операции с треками, включая управление объектами в треках
    через объектный сервис. Поддерживает полное жизненное управление треками
    с сохранением целостности данных и порядковых номеров объектов.
    """

    def __init__(self, objects_service:ObjectsService):
        """
        Инициализация сервиса треков.

        Args:
            objects_service: Сервис для работы с объектами
        """
        self.objects_service = objects_service

    def delete_track(self, conn, track_id: int) -> bool:
        """
        Каскадно удаляет трек и все связанные с ним объекты.

        Args:
            conn: Соединение с базой данных
            track_id: ID трека для удаления

        Returns:
            True если удаление успешно, False если трек не найден
        """
        cursor = conn.cursor()

        # Проверяем существование трека
        cursor.execute("SELECT id FROM track WHERE id = ?", (track_id,))
        if not cursor.fetchone():
            return False

        # Получаем все объекты трека для каскадного удаления
        cursor.execute("SELECT object_id FROM object_to_track WHERE track_id = ?", (track_id,))
        object_ids = [row['object_id'] for row in cursor.fetchall()]

        # Удаляем объекты через objects_service
        for object_id in object_ids:
            self.objects_service.delete_object(conn, object_id)

        # Удаляем записи из object_to_track
        cursor.execute("DELETE FROM object_to_track WHERE track_id = ?", (track_id,))

        # Удаляем сам трек
        cursor.execute("DELETE FROM track WHERE id = ?", (track_id,))

        logging.info(f"Трек {track_id} и все связанные объекты успешно удалены")
        return True

    def add_track(self, conn, track: Track, step_id: int) -> Track:
        """
        Каскадно добавляет трек и все связанные с ним объекты.

        Args:
            conn: Соединение с базой данных
            track: Объект трека для добавления
            step_id: ID шага, к которому привязан трек

        Returns:
            Объект Track с заполненным ID и ID объектов
        """
        cursor = conn.cursor()

        # Добавляем основной трек
        cursor.execute('''
            INSERT INTO track (step_id)
            VALUES (?)
        ''', (step_id,))

        track_id = cursor.lastrowid
        track.id = track_id

        # Добавляем объекты трека через objects_service
        self._add_track_objects(conn, track_id, track)

        # Получаем полный трек с заполненными ID объектов
        result = self.get_track_by_id(conn, track_id)
        logging.info(f"Трек {track_id} успешно добавлен")
        return result

    def get_track_by_id(self, conn, track_id: int) -> Optional[Track]:
        """
        Получает трек по ID со всеми связанными объектами.

        Args:
            conn: Соединение с базой данных
            track_id: ID трека

        Returns:
            Объект Track с заполненными SMs и PSs или None если не найден
        """
        cursor = conn.cursor()

        # Получаем основную информацию о треке
        cursor.execute("SELECT * FROM track WHERE id = ?", (track_id,))
        track_row = cursor.fetchone()

        if not track_row:
            return None

        # Создаем объект трека
        track = Track(
            id=track_row['id']
        )

        # Загружаем объекты трека с порядковыми номерами
        track_objects = self.objects_service.get_objects_by_track(conn, track_id)

        # Разделяем объекты на SMs и PSs по типу класса
        for obj, _ in track_objects:
            if obj.class_ref.type == CLASS_TYPES.SM.value:
                track.SMs.append(obj)
            elif obj.class_ref.type == CLASS_TYPES.PS.value:
                track.PSs.append(obj)

        # Сортируем по порядковому номеру
        track.SMs.sort(key=lambda x: next((num for obj, num in track_objects if obj.id == x.id), 0))

        return track

    def update_track(self, conn, track: Track) -> Track:
        """
        Точечно обновляет трек и его объекты.

        Args:
            conn: Соединение с базой данных
            track: Объект трека с обновленными данными

        Returns:
            Обновленный объект Track
        """
        if not track.id:
            raise ValueError("Track ID is required for update")

        cursor = conn.cursor()

        # Проверяем существование трека
        cursor.execute("SELECT id FROM track WHERE id = ?", (track.id,))
        if not cursor.fetchone():
            raise ValueError(f"Track with ID {track.id} not found")

        # Получаем текущую версию трека
        current_track = self.get_track_by_id(conn, track.id)
        if not current_track:
            raise ValueError(f"Track with ID {track.id} not found")

        # Точечно обновляем объекты трека
        self._update_track_objects(conn, track.id, track, current_track)

        # Получаем обновленный трек
        result = self.get_track_by_id(conn, track.id)
        logging.info(f"Трек {track.id} успешно обновлен")
        return result

    def _add_track_objects(self, conn, track_id: int, track: Track):
        """
        Добавляет объекты трека в правильном порядке.

        Args:
            conn: Соединение с базой данных
            track_id: ID трека
            track: Объект трека с SMs и PSs
        """
        num_in_track = 0

        # Добавляем SMs
        for sm in track.SMs:
            # Если объект еще не сохранен в базе - добавляем
            if not sm.id:
                added_sm = self.objects_service.add_object(conn, sm, track_id=track_id, num_in_track=num_in_track)
                sm.id = added_sm.id
            else:
                # Если объект уже существует - обновляем связь
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO object_to_track (track_id, object_id, num_in_track)
                    VALUES (?, ?, ?)
                ''', (track_id, sm.id, num_in_track))
            num_in_track += 1

        # Добавляем PSs
        for ps in track.PSs:
            # Если объект еще не сохранен в базе - добавляем
            if not ps.id:
                added_ps = self.objects_service.add_object(conn, ps, track_id=track_id, num_in_track=num_in_track)
                ps.id = added_ps.id
            else:
                # Если объект уже существует - обновляем связь
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO object_to_track (track_id, object_id, num_in_track)
                    VALUES (?, ?, ?)
                ''', (track_id, ps.id, num_in_track))
            num_in_track += 1

    def _update_track_objects(self, conn, track_id: int, new_track: Track, current_track: Track):
        # 1. Собираем ID из старого трека
        current_sm_ids = {sm.id for sm in current_track.SMs if sm.id}
        current_ps_ids = {ps.id for ps in current_track.PSs if ps.id}

        # 2. Находим ID для удаления
        deleted_sm_ids = current_sm_ids - {sm.id for sm in new_track.SMs if sm.id}
        deleted_ps_ids = current_ps_ids - {ps.id for ps in new_track.PSs if ps.id}

        # 3. Удаляем лишние объекты
        for obj_id in deleted_sm_ids:
            self.objects_service.delete_object(conn, obj_id)
        for obj_id in deleted_ps_ids:
            self.objects_service.delete_object(conn, obj_id)

        # 4. Обрабатываем SMs: добавляем/обновляем с num_in_track
        for idx, sm in enumerate(new_track.SMs):
            num_in_track = idx + 1

            if sm.id and sm.id in current_sm_ids:
                updated_sm = self.objects_service.update_object(
                    conn, sm, num_in_track=num_in_track
                )
                new_track.SMs[idx] = updated_sm  # Сохраняем актуальный объект
            else:
                added_sm = self.objects_service.add_object(
                    conn, sm, track_id=track_id, num_in_track=num_in_track
                )
                new_track.SMs[idx] = added_sm  # Сохраняем актуальный объект

        # 5. Обрабатываем PSs: добавляем/обновляем (без num_in_track)
        for idx, ps in enumerate(new_track.PSs):
            if ps.id and ps.id in current_ps_ids:
                updated_ps = self.objects_service.update_object(conn, ps)
                new_track.PSs[idx] = updated_ps  # Сохраняем актуальный объект!
            else:
                added_ps = self.objects_service.add_object(conn, ps, track_id=track_id)
                new_track.PSs[idx] = added_ps  # Сохраняем актуальный объект!

from CORE.db_dataclasses import Parameter



import sqlite3
from typing import List, Optional


class ParamsRepo:
    """Репозиторий для работы с параметрами (работает только через переданные соединения)"""

    def add_new_param(self, conn: sqlite3.Connection, form_id: int, param: Parameter) -> Optional[int]:
        """
        Добавляет один новый параметр к форме.
        Возвращает ID созданного параметра или None при ошибке.
        """
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO parameters 
                (form_id, name, comment)
                VALUES (?, ?, ?)
            """, (form_id, param.name, param.comment))

            param_id = cursor.lastrowid
            print(f"Добавлен параметр с ID {param_id} к форме {form_id}")
            return param_id

        except sqlite3.IntegrityError as e:
            print(f"Ошибка целостности при добавлении параметра к форме {form_id}: {e}")
            return None
        except Exception as e:
            print(f"Ошибка при добавлении параметра к форме {form_id}: {e}")
            return None
        finally:
            cursor.close()



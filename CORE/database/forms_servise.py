from CORE.db_dataclasses import Form, Track, Point,  Parameter, BaseClass, BasePazzle
from CORE.database.db_manager import DBManager
from CORE.database.repositories import *


from typing import List, Optional, Dict
import logging

class FormsServise:
    def __init__(self, db: DBManager) -> None:

        self.db = db
        self._points_repo = PointsRepo()
        self._simple_fprms_repo = FormsSimpleRepo()
        self._params_repo = ParamsRepo()


    def add_new_form(self, form: Form) -> Optional[int]:
        """Сохранение формы в базу данных в одной транзакции"""
        conn = self.db.get_connection()

        try:
            form_id = self._simple_fprms_repo.add_form(conn=conn, form=Form)
            if not form_id:
                conn.rollback()
                return None
            conn.commit()
            return form_id

        except Exception as e:
            conn.rollback()
            logging.error(f"Ошибка создания формы '{form.name}': {e}")
            return None

        finally:
            conn.close()


# Пример использования
if __name__ == "__main__":
    db_manager = DBManager()

    if db_manager.db_exists():
        db_manager.delete_database()
    db_manager.create_tables()


    servise = FormsServise(db_manager)

    test_form = Form(name="test_form",
                     comment="комментарий",
                     path_to_pic="\путь к картике",
                     path_to_dataset="\путь к датасету")

    id = servise.add_new_form(test_form)
    print(id)
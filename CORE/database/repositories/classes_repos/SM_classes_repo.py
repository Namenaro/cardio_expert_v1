from CORE.dataclasses import Form, SM_Class, PS_Class, PC_Class, HC_Class
from CORE.dataclasses.pazzles import ConstructorArg
from CORE.database.db_manager import DBManager
from CORE.dataclasses.pazzles import CLASS_TYPES


from typing import List, Optional
from copy import deepcopy


class SM_ClassesRepo:
    """Репозиторий для работы с классами типа SM"""

    def __init__(self, db: DBManager) -> None:
        """Инициализация репозитория"""
        self.db = db

    def add_new_SM_class(self, name: str, comment: str,
                         constructor_args: List[ConstructorArg]) -> int:
        """
        Добавляет новый класс в базу данных

        Args:
            name: Имя класса
            comment: Комментарий к классу
            constructor_args: Список аргументов конструктора

        Returns:
            ID созданного класса
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Создаем класс
            cursor.execute(
                "INSERT INTO class (name, comment, TYPE) VALUES (?, ?, ?)",
                (name, comment, CLASS_TYPES.SM.value)
            )
            class_id = cursor.lastrowid

            # Добавляем аргументы конструктора
            for arg in constructor_args:
                cursor.execute(
                    "INSERT INTO argument_to_class (class_id, name, comment, data_type, default_value) VALUES (?, ?, ?, ?, ?)",
                    (class_id, arg.name, arg.comment, arg.data_type, arg.default_val)
                )

            conn.commit()

            return class_id

        except Exception:
            conn.rollback()
            raise

    def delete_SM_class(self, class_id: int) -> bool:
        """
        Удаляет класс по ID (автоматически удаляет связанные аргументы)

        Args:
            class_id: ID класса для удаления

        Returns:
            True если класс удален, False если класс не найден
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM class WHERE id = ?", (class_id,))
        success = cursor.rowcount > 0
        conn.commit()
        return success

    def update_SM_class(self, sm_class: SM_Class) -> bool:
        """
        Обновляет данные класса

        Args:
            sm_class: Объект класса с обновленными данными

        Returns:
            True если класс обновлен, False если класс не найден
        """
        if sm_class.id is None:
            raise ValueError("Class ID must be provided for update")

        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Обновляем данные класса
            cursor.execute(
                "UPDATE class SET name = ?, comment = ?  WHERE id = ?",
                (sm_class.name, sm_class.comment, sm_class.id)
            )

            if cursor.rowcount == 0:
                conn.rollback()
                return False

            # Удаляем старые аргументы и добавляем новые
            cursor.execute("DELETE FROM argument_to_class WHERE class_id = ?", (sm_class.id,))

            for arg in sm_class.constructor_args:
                cursor.execute(
                    "INSERT INTO argument_to_class (class_id, name, comment, data_type, default_value) VALUES (?, ?, ?, ?, ?)",
                    (sm_class.id, arg.name, arg.comment, arg.data_type, arg.default_val)
                )

            conn.commit()
            return True

        except Exception:
            conn.rollback()
            raise

    def get_SM_class_by_id(self, class_id: int) -> Optional[SM_Class]:
        """
        Получает класс по ID вместе с аргументами (вспомогательный метод)

        Args:
            class_id: ID класса для поиска

        Returns:
            Объект класса с аргументами или None если не найден
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Получаем данные класса
        cursor.execute(
            "SELECT id, name, comment FROM class WHERE id = ? AND TYPE = ?",
            (class_id, CLASS_TYPES.SM.value)
        )
        row = cursor.fetchone()

        if not row:
            return None

        # Получаем аргументы класса
        cursor.execute(
            "SELECT id, name, comment, data_type, default_value FROM argument_to_class WHERE class_id = ?",
            (class_id,)
        )
        args_rows = cursor.fetchall()

        # Собираем аргументы
        constructor_args = []
        for arg_row in args_rows:
            arg = ConstructorArg(
                id=arg_row[0],
                name=arg_row[1],
                comment=arg_row[2] or "",
                data_type=arg_row[3],
                default_val=arg_row[4] or ""
            )
            constructor_args.append(arg)

        # Собираем класс
        sm_class = SM_Class(
            id=row[0],
            name=row[1],
            comment=row[2] or "",
            constructor_args=constructor_args
        )

        return sm_class

    def get_all_SM_classes(self) -> List[SM_Class]:
        """
        Получает все классы (вспомогательный метод)

        Returns:
            Список всех классов
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM class WHERE TYPE = ?",
                       (CLASS_TYPES.SM.value,))
        class_ids = [row[0] for row in cursor.fetchall()]

        classes = []
        for class_id in class_ids:
            sm_class = self.get_SM_class_by_id(class_id)
            if sm_class:
                classes.append(sm_class)

        return classes


if __name__ == "__main__":
    db_manager = DBManager()

    if db_manager.db_exists():
        db_manager.delete_database()
    db_manager.create_tables()


    repo = SM_ClassesRepo(db_manager)

    # 1. Добавление нового класса
    constructor_args = [
        ConstructorArg(name="param1", comment="Первый параметр", data_type="string", default_val="default1"),
        ConstructorArg(name="param2", comment="Второй параметр", data_type="int", default_val="42")
    ]

    class_id = repo.add_new_SM_class(
        name="TestClassSM",
        comment="Тестовый класс",
        constructor_args=constructor_args
    )
    print("Добавлен SM-класс " + str(class_id))

    # 2. Получение всех классов этого типа
    classes = repo.get_all_SM_classes()
    print(classes)

    # 3. Модификация существующего класса
    modified = deepcopy(classes[0])
    modified.name = "new_name!"
    repo.update_SM_class(sm_class=modified)

    # 4. Получение класса по его id
    obj = repo.get_SM_class_by_id(class_id=class_id)
    print(obj)

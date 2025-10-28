from CORE.settings import DB_PATH
from CORE.database.connection import DatabaseConnection
import os

class Schema:
    """Класс для управления схемой базы данных: ее создание и удаление"""

    def __init__(self) -> None:
        self.db = DatabaseConnection()

    def db_exists(self) -> bool:
        """
        Проверяет существование базы данных

        Returns:
            True если база существует, False если нет
        """
        return os.path.exists(DB_PATH)

    def create_tables(self) -> None:
        """Создает все таблицы в базе данных"""
        connection = self.db.get_connection()
        cursor = connection.cursor()

        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS form (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                comment TEXT,
                                name TEXT NOT NULL UNIQUE,
                                path_to_pic TEXT,
                                path_to_dataset TEXT
                            )
                            ''')

        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS parameter (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                form_id INTEGER,
                                comment TEXT,
                                weight_of_param_for_exemplar_evaluation REAL,
                                FOREIGN KEY (form_id) REFERENCES form(id)
                                ON UPDATE NO ACTION ON DELETE NO ACTION

                            )
                            ''')

        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS point (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                comment TEXT NOT NULL DEFAULT '""',
                                form_id INTEGER,
                                FOREIGN KEY (form_id) REFERENCES form(id)
                                ON UPDATE NO ACTION ON DELETE NO ACTION
                            )
                            ''')

        cursor.execute('''
        
                        CREATE TABLE IF NOT EXISTS class (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE,
                            comment TEXT,
                            TYPE TEXT
                        )
                    ''')

        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS object (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            class_id INTEGER NOT NULL,
                            name TEXT,
                            comment TEXT
                        )
                        ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS HC_object_to_form (
            	        id INTEGER PRIMARY KEY AUTOINCREMENT,
            	        form_id INTEGER NOT NULL,
            	        object_id INTEGER NOT NULL,
            	        FOREIGN KEY (form_id) REFERENCES form(id)
            	        ON UPDATE NO ACTION ON DELETE NO ACTION,
            	        FOREIGN KEY (object_id) REFERENCES object(id)
            	        ON UPDATE NO ACTION ON DELETE NO ACTION
                    );
                    ''')

        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS PC_object_to_form (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                form_id INTEGER NOT NULL,
                                object_id INTEGER NOT NULL,
                                FOREIGN KEY (object_id) REFERENCES object(id)
                                ON UPDATE NO ACTION ON DELETE NO ACTION,
                                FOREIGN KEY (form_id) REFERENCES form(id)
                                ON UPDATE NO ACTION ON DELETE NO ACTION
                            )
                            ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS step (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        form_id INTEGER,
                        target_point_id INTEGER,
                        left_point_id INTEGER,
                        right_point_id INTEGER,
                        left_padding REAL,
                        right_padding REAL,
                        comment TEXT,
                        num_in_form INTEGER NOT NULL,
                        FOREIGN KEY (right_point_id) REFERENCES point(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (left_point_id) REFERENCES point(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (target_point_id) REFERENCES point(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (form_id) REFERENCES form(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')


        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS track (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        step_id INTEGER,
                        FOREIGN KEY (step_id) REFERENCES step(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS argument_to_class (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        comment TEXT,
                        data_type TEXT NOT NULL,
                        default_value TEXT,
                        FOREIGN KEY (class_id) REFERENCES class(id)
                        ON UPDATE CASCADE ON DELETE CASCADE
                    )
                    ''')

        cursor.execute('''  
                    CREATE TABLE IF NOT EXISTS value_to_argument (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        object_id INTEGER,
                        argument_id INTEGER NOT NULL,
                        argument_value TEXT,
                        FOREIGN KEY (argument_id) REFERENCES argument(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (object_id) REFERENCES object(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                        
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS input_param_to_class (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        comment TEXT,
                        FOREIGN KEY (class_id) REFERENCES class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                            CREATE TABLE IF NOT EXISTS input_point_to_class (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                class_id INTEGER NOT NULL,
                                name TEXT NOT NULL,
                                comment TEXT,
                                FOREIGN KEY (class_id) REFERENCES class(id)
                                ON UPDATE NO ACTION ON DELETE NO ACTION
                               
                            )
                            ''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS output_param_to_class (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        class_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        comment TEXT,
                        FOREIGN KEY (class_id) REFERENCES class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS object_to_track (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        track_id INTEGER,
                        object_id INTEGER,
                        num_in_track INTEGER NOT NULL,
                        FOREIGN KEY (object_id) REFERENCES object(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (track_id) REFERENCES track(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS value_to_output_param (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        object_id INTEGER NOT NULL,
                        output_param_id INTEGER NOT NULL,
                        parameter_id INTEGER NOT NULL,
                        FOREIGN KEY (parameter_id) REFERENCES parameter(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (output_param_id) REFERENCES output_param_to_class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (object_id) REFERENCES object(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS value_to_input_param (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        object_id INTEGER,
                        input_param_id INTEGER NOT NULL,
                        parameter_id INTEGER,
                        FOREIGN KEY (input_param_id) REFERENCES input_param_to_class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (object_id) REFERENCES object(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (parameter_id) REFERENCES parameter(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS value_to_input_point (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        object_id INTEGER NOT NULL,
                        input_point_id INTEGER NOT NULL,
                        point_id INTEGER NOT NULL,
                        FOREIGN KEY (object_id) REFERENCES object(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (input_point_id) REFERENCES input_points_to_class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (point_id) REFERENCES points(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        connection.commit()
        self.db.close()
        print(print("Таблицы успешно созданы"))

    def delete_database(self) -> bool:
        """
        Удаляет базу данных

        Returns:
            True если база удалена, False если не существовала
        """
        self.db.close()
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            return True
        return False





if __name__ == "__main__":
    schema= Schema()
    schema.create_tables()
    #if schema.db_exists():
        #schema.delete_database()

    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()
    # Проверим какие таблицы уже есть
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    print(f"Существующие таблицы: {existing_tables}")




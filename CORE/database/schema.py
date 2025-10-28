from CORE.settings import DB_PATH
from connection import DatabaseConnection
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
                    CREATE TABLE IF NOT EXISTS HC_object_to_form (
            	        id INTEGER NOT NULL UNIQUE,
            	        form_id INTEGER NOT NULL,
            	        object_id INTEGER NOT NULL,
            	        PRIMARY KEY(id),
            	        FOREIGN KEY (id) REFERENCES form(id)
            	        ON UPDATE NO ACTION ON DELETE NO ACTION
                    );
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS step (
                        id INTEGER NOT NULL UNIQUE,
                        form_id INTEGER,
                        target_point_id INTEGER,
                        left_point_id INTEGER,
                        right_point_id INTEGER,
                        left_padding REAL,
                        right_padding REAL,
                        comment TEXT,
                        num_in_form INTEGER NOT NULL,
                        PRIMARY KEY(id),
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
                    CREATE INDEX IF NOT EXISTS step_index_0
                    ON step (id)
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS form (
                        id INTEGER NOT NULL UNIQUE,
                        comment TEXT,
                        name TEXT NOT NULL UNIQUE,
                        path_to_pic TEXT,
                        path_to_dataset TEXT,
                        PRIMARY KEY(id)
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS point (
                        id INTEGER NOT NULL UNIQUE,
                        name TEXT NOT NULL,
                        comment TEXT NOT NULL DEFAULT '""',
                        form_id INTEGER,
                        PRIMARY KEY(id),
                        FOREIGN KEY (id) REFERENCES value_to_input_point(point_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (form_id) REFERENCES form(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS parameter (
                        id INTEGER NOT NULL UNIQUE,
                        name TEXT NOT NULL,
                        form_id INTEGER,
                        comment TEXT,
                        weight_of_param_for_exemplar_evaluation REAL,
                        PRIMARY KEY(id),
                        FOREIGN KEY (form_id) REFERENCES form(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (id) REFERENCES value_to_input_param(parameter_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS track (
                        id INTEGER NOT NULL UNIQUE,
                        step_id INTEGER,
                        PRIMARY KEY(id),
                        FOREIGN KEY (step_id) REFERENCES step(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (id) REFERENCES object_to_track(track_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS argument_to_class (
                        id INTEGER NOT NULL UNIQUE,
                        class_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        comment TEXT,
                        data_type TEXT NOT NULL,
                        default_value TEXT,
                        PRIMARY KEY(id),
                        FOREIGN KEY (class_id) REFERENCES class(id)
                        ON UPDATE CASCADE ON DELETE CASCADE
                    )
                    ''')

        cursor.execute('''  
                    CREATE TABLE IF NOT EXISTS value_to_argument (
                        id INTEGER NOT NULL UNIQUE,
                        object_id INTEGER,
                        argument_id INTEGER NOT NULL,
                        argument_value TEXT,
                        PRIMARY KEY(id),
                        FOREIGN KEY (argument_id) REFERENCES argument_to_class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS class (
                        id INTEGER NOT NULL UNIQUE,
                        name TEXT NOT NULL UNIQUE,
                        comment TEXT,
                        TYPE TEXT,
                        PRIMARY KEY(id),
                        FOREIGN KEY (id) REFERENCES output_param_to_class(class_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS object (
                        id INTEGER NOT NULL UNIQUE,
                        class_id INTEGER NOT NULL,
                        name TEXT,
                        comment TEXT,
                        PRIMARY KEY(id),
                        FOREIGN KEY (id) REFERENCES HC_object_to_form(object_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (id) REFERENCES value_to_argument(object_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (id) REFERENCES value_to_output_param(object_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (id) REFERENCES value_to_input_param(object_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (id) REFERENCES value_to_input_point(object_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (class_id) REFERENCES class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS object_to_track (
                        id INTEGER NOT NULL UNIQUE,
                        track_id INTEGER,
                        object_id INTEGER,
                        num_in_track INTEGER NOT NULL,
                        PRIMARY KEY(id),
                        FOREIGN KEY (object_id) REFERENCES object(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS PC_object_to_form (
                        id INTEGER NOT NULL UNIQUE,
                        form_id INTEGER NOT NULL,
                        object_id INTEGER NOT NULL,
                        PRIMARY KEY(id),
                        FOREIGN KEY (object_id) REFERENCES object(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (form_id) REFERENCES form(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS input_param_to_class (
                        id INTEGER NOT NULL UNIQUE,
                        class_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        comment TEXT,
                        PRIMARY KEY(id),
                        FOREIGN KEY (id) REFERENCES class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS input_point_to_class (
                        id INTEGER NOT NULL UNIQUE,
                        class_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        comment TEXT,
                        PRIMARY KEY(id),
                        FOREIGN KEY (class_id) REFERENCES class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (id) REFERENCES value_to_input_point(input_point_id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS output_param_to_class (
                        id INTEGER NOT NULL UNIQUE,
                        class_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        comment TEXT,
                        PRIMARY KEY(id)
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS value_to_output_param (
                        id INTEGER NOT NULL UNIQUE,
                        object_id INTEGER NOT NULL,
                        output_param_id INTEGER NOT NULL,
                        parameter_id INTEGER NOT NULL,
                        PRIMARY KEY(id),
                        FOREIGN KEY (parameter_id) REFERENCES parameter(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION,
                        FOREIGN KEY (output_param_id) REFERENCES output_param_to_class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS value_to_input_param (
                        id INTEGER NOT NULL UNIQUE,
                        object_id INTEGER,
                        input_param_id INTEGER NOT NULL,
                        parameter_id INTEGER,
                        PRIMARY KEY(id),
                        FOREIGN KEY (input_param_id) REFERENCES input_param_to_class(id)
                        ON UPDATE NO ACTION ON DELETE NO ACTION
                    )
                    ''')

        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS value_to_input_point (
                        id INTEGER NOT NULL UNIQUE,
                        object_id INTEGER NOT NULL,
                        input_point_id INTEGER NOT NULL,
                        point_id INTEGER NOT NULL,
                        PRIMARY KEY(id)
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




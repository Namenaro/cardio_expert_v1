import sqlite3

from sqlalchemy import create_engine, MetaData
from sqlalchemy_schemadisplay import create_schema_graph
from tabulate import tabulate


class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def connect(self):
        """Установка соединения с базой данных"""
        self.connection = sqlite3.connect(self.db_name)
        return self.connection.cursor()

    def create_tables(self):
        """Создание всех необходимых таблиц"""
        cursor = self.connect()
        cursor.execute("PRAGMA foreign_keys = ON")

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "HC_object_to_form" (
	        "id" INTEGER NOT NULL UNIQUE,
	        "form_id" INTEGER NOT NULL,
	        "object_id" INTEGER NOT NULL,
	        PRIMARY KEY("id"),
	        FOREIGN KEY ("id") REFERENCES "form"("id")
	        ON UPDATE NO ACTION ON DELETE NO ACTION
        );
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "step" (
            "id" INTEGER NOT NULL UNIQUE,
            "form_id" INTEGER,
            "target_point_id" INTEGER,
            "left_point_id" INTEGER,
            "right_point_id" INTEGER,
            "left_padding" REAL,
            "right_padding" REAL,
            "comment" TEXT,
            "num_in_form" INTEGER NOT NULL,
            PRIMARY KEY("id"),
            FOREIGN KEY ("right_point_id") REFERENCES "point"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("left_point_id") REFERENCES "point"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("target_point_id") REFERENCES "point"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("form_id") REFERENCES "form"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE INDEX IF NOT EXISTS "step_index_0"
        ON "step" (id)
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "form" (
            "id" INTEGER NOT NULL UNIQUE,
            "comment" TEXT,
            "name" TEXT NOT NULL UNIQUE,
            "path_to_pic" TEXT UNIQUE,
            "path_to_dataset" TEXT UNIQUE,
            PRIMARY KEY("id")
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "point" (
            "id" INTEGER NOT NULL UNIQUE,
            "name" TEXT NOT NULL,
            "comment" TEXT NOT NULL DEFAULT '""',
            "form_id" INTEGER,
            PRIMARY KEY("id"),
            FOREIGN KEY ("id") REFERENCES "value_to_input_point"("point_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("form_id") REFERENCES "form"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "parameter" (
            "id" INTEGER NOT NULL UNIQUE,
            "name" TEXT NOT NULL,
            "form_id" INTEGER,
            "comment" TEXT,
            "weight_of_param_for_exemplar_evaluation" REAL,
            PRIMARY KEY("id"),
            FOREIGN KEY ("form_id") REFERENCES "form"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("id") REFERENCES "value_to_input_param"("parameter_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "track" (
            "id" INTEGER NOT NULL UNIQUE,
            "step_id" INTEGER,
            PRIMARY KEY("id"),
            FOREIGN KEY ("step_id") REFERENCES "step"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("id") REFERENCES "object_to_track"("track_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "argument_to_class" (
            "id" INTEGER NOT NULL UNIQUE,
            "class_id" INTEGER NOT NULL,
            "name" TEXT NOT NULL,
            "comment" TEXT,
            "data_type" TEXT NOT NULL,
            "default_value" TEXT,
            PRIMARY KEY("id"),
            FOREIGN KEY ("class_id") REFERENCES "class"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''  
        CREATE TABLE IF NOT EXISTS "value_to_argument" (
            "id" INTEGER NOT NULL UNIQUE,
            "object_id" INTEGER,
            "argument_id" INTEGER NOT NULL,
            "argument_value" TEXT,
            PRIMARY KEY("id"),
            FOREIGN KEY ("argument_id") REFERENCES "argument_to_class"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "class" (
            "id" INTEGER NOT NULL UNIQUE,
            "name" TEXT NOT NULL UNIQUE,
            "comment" TEXT,
            "TYPE" TEXT,
            PRIMARY KEY("id"),
            FOREIGN KEY ("id") REFERENCES "output_param_to_class"("class_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "object" (
            "id" INTEGER NOT NULL UNIQUE,
            "class_id" INTEGER NOT NULL,
            "name" TEXT,
            "comment" TEXT,
            PRIMARY KEY("id"),
            FOREIGN KEY ("id") REFERENCES "HC_object_to_form"("object_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("id") REFERENCES "value_to_argument"("object_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("id") REFERENCES "value_to_output_param"("object_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("id") REFERENCES "value_to_input_param"("object_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("id") REFERENCES "value_to_input_point"("object_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("class_id") REFERENCES "class"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "object_to_track" (
            "id" INTEGER NOT NULL UNIQUE,
            "track_id" INTEGER,
            "object_id" INTEGER,
            "num_in_track" INTEGER NOT NULL,
            PRIMARY KEY("id"),
            FOREIGN KEY ("object_id") REFERENCES "object"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "PC_object_to_form" (
            "id" INTEGER NOT NULL UNIQUE,
            "form_id" INTEGER NOT NULL,
            "object_id" INTEGER NOT NULL,
            PRIMARY KEY("id"),
            FOREIGN KEY ("object_id") REFERENCES "object"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("form_id") REFERENCES "form"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "input_param_to_class" (
            "id" INTEGER NOT NULL UNIQUE,
            "class_id" INTEGER NOT NULL,
            "name" TEXT NOT NULL,
            "comment" TEXT,
            PRIMARY KEY("id"),
            FOREIGN KEY ("id") REFERENCES "class"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "input_point_to_class" (
            "id" INTEGER NOT NULL UNIQUE,
            "class_id" INTEGER NOT NULL,
            "name" TEXT NOT NULL,
            "comment" TEXT,
            PRIMARY KEY("id"),
            FOREIGN KEY ("class_id") REFERENCES "class"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("id") REFERENCES "value_to_input_point"("input_point_id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "output_param_to_class" (
            "id" INTEGER NOT NULL UNIQUE,
            "class_id" INTEGER NOT NULL,
            "name" TEXT NOT NULL,
            "comment" TEXT,
            PRIMARY KEY("id")
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "value_to_output_param" (
            "id" INTEGER NOT NULL UNIQUE,
            "object_id" INTEGER NOT NULL,
            "output_param_id" INTEGER NOT NULL,
            "parameter_id" INTEGER NOT NULL,
            PRIMARY KEY("id"),
            FOREIGN KEY ("parameter_id") REFERENCES "parameter"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION,
            FOREIGN KEY ("output_param_id") REFERENCES "output_param_to_class"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "value_to_input_param" (
            "id" INTEGER NOT NULL UNIQUE,
            "object_id" INTEGER,
            "input_param_id" INTEGER NOT NULL,
            "parameter_id" INTEGER,
            PRIMARY KEY("id"),
            FOREIGN KEY ("input_param_id") REFERENCES "input_param_to_class"("id")
            ON UPDATE NO ACTION ON DELETE NO ACTION
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS "value_to_input_point" (
            "id" INTEGER NOT NULL UNIQUE,
            "object_id" INTEGER NOT NULL,
            "input_point_id" INTEGER NOT NULL,
            "point_id" INTEGER NOT NULL,
            PRIMARY KEY("id")
        )
        ''')

        self.connection.commit()
        print("Таблицы успешно созданы")

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.connection:
            self.connection.close()

    def generate_er_diagram(self, output_file='database_er_diagram.png'):
        """Генерация ER-диаграммы базы данных"""

        try:
            # Создаем подключение через SQLAlchemy
            engine = create_engine(f'sqlite:///{self.db_name}')

            # Создаем метаданные и загружаем структуру базы
            metadata = MetaData()
            metadata.reflect(bind=engine)

            # Создаем граф схемы с указанием метаданных
            graph = create_schema_graph(
                metadata=metadata,
                engine=engine,
                show_datatypes=True,
                show_indexes=False,
                rankdir='TB',
                concentrate=False
            )

            # Сохраняем в PNG
            graph.write_png(output_file)
            print(f"ER-диаграмма сохранена как: {output_file}")

        except Exception as e:
            print(f"Ошибка при создании диаграммы: {e}")

    def add_record(self, table_name, **kwargs):
        """Универсальный метод для добавления записи в любую таблицу"""
        cursor = self.connect()
        try:
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['?' for _ in kwargs])
            values = tuple(kwargs.values())

            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
            self.connection.commit()

            record_id = cursor.lastrowid
            print(f"Добавлена запись в '{table_name}' (ID: {record_id})")
            return record_id

        except sqlite3.Error as e:
            print(f"Ошибка добавления в '{table_name}': {e}")
            self.connection.rollback()
            return None
        finally:
            if self.connection:
                cursor.close()

    def delete_record_by_id(self, table_name, record_id):
        """Удаление записи по id"""

        cursor = self.connect()
        try:
            find_record_sql = f"SELECT * FROM {table_name} WHERE id = ?"
            cursor.execute(find_record_sql, (record_id,))
            existing_record = cursor.fetchone()

            if not existing_record:
                print(f"Запись с id = {record_id} не найдена в базе данных")
                return False

            sql = f"DELETE FROM {table_name} WHERE id= ?"
            cursor.execute(sql, (record_id,))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Ошибка удаления: {e}")
        finally:
            if self.connection:
                cursor.close()

    def show_table(self, table_name, limit=10, where_clause=""):
        """Вывод содержимого таблицы"""
        cursor = self.connect()
        try:
            # Получаем названия колонок
            cursor.execute(f"PRAGMA table_info({table_name})")
            # columns_info = cursor.fetchall()
            # column_names = [col[1] for col in columns_info]

            # Формируем SQL запрос
            sql = f"SELECT * FROM {table_name}"
            if where_clause:
                sql += f" WHERE {where_clause}"
            sql += f" LIMIT {limit}"

            # Выполняем запрос
            cursor.execute(sql)
            rows = cursor.fetchall()

            if not rows:
                print(f"Таблица '{table_name}' пуста")
                return

            headers = [description[0] for description in cursor.description]

            # Выводим результат
            print(f"\nТаблица: {table_name}")
            print(f"Всего записей: {len(rows)}")
            print("=" * 80)
            print(tabulate(rows, headers=headers, tablefmt="grid"))


        except sqlite3.Error as e:
            print(f"Ошибка чтения таблицы '{table_name}': {e}")
        finally:
            if self.connection:
                self.connection.close()


db = DatabaseManager("test.db")
# db.create_tables()
# db.add_record("point", name="NewPoint", comment="NewPoint")
# db.close()

# Вывод таблицы по названию
# db.show_table("step")

# Генерация изображения структуры бд
# db.generate_er_diagram()

#Добавление новой записи
# db.add_record("form",
#               comment= "пу пу пу",
#               name="some_test_form1",
#               path_to_pic="/form1.jpg",
#               path_to_dataset="/dataset1.csv")

# db.show_table(table_name="form")

# Удаление записи по id
# db.delete_record_by_id(table_name="form", record_id=3)
db.show_table(table_name="form")
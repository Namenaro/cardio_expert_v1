from CORE.settings import DB_PATH

from sqlalchemy import create_engine, MetaData
from sqlalchemy_schemadisplay import create_schema_graph

def generate_er_diagram(output_file='database_er_diagram.png'):
    """Генерация ER-диаграммы базы данных"""

    try:
        # Создаем подключение через SQLAlchemy
        engine = create_engine(f'sqlite:///{DB_PATH}')

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


if __name__ == "__main__":
    from CORE.database.schema import Schema
    schema = Schema()
    if not schema.db_exists():
        schema.create_tables()

    generate_er_diagram()



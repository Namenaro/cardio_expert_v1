from CORE.settings import DB_PATH
import os
import sqlite3
import graphviz


def generate_er_diagram_sqlite(output_file='database_er_diagram'):
    """Генерация ER-диаграммы с использованием sqlite3 и graphviz"""

    try:
        if not os.path.exists(DB_PATH):
            print(f"База данных {DB_PATH} не существует")
            return

        print(f"Создание диаграммы для базы: {DB_PATH}")

        # Создаем граф
        dot = graphviz.Digraph(
            comment='Database ER Diagram',
            format='png',
            graph_attr={
                'rankdir': 'TB',
                'splines': 'ortho',
                'overlap': 'false'
            },
            node_attr={'shape': 'plaintext'}
        )

        # Подключаемся к базе
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем список пользовательских таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        print(f"Найдено таблиц: {len(tables)}")

        # Создаем узлы для таблиц
        for table in tables:
            print(f"Обрабатываем таблицу: {table}")

            # Получаем колонки таблицы
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            # Создаем HTML-таблицу для узла
            label = '''<<TABLE BORDER="1" CELLBORDER="0" CELLSPACING="0" CELLPADDING="4">
            <TR><TD BGCOLOR="lightblue" COLSPAN="2"><B>''' + table + '''</B></TD></TR>'''

            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                constraints = []
                if pk:
                    constraints.append("PK")
                if not_null:
                    constraints.append("NN")

                constraint_str = " (" + ", ".join(constraints) + ")" if constraints else ""
                label += f'<TR><TD ALIGN="LEFT">{col_name}</TD><TD ALIGN="LEFT">{col_type}{constraint_str}</TD></TR>'

            label += "</TABLE>>"

            dot.node(table, label=label)

        # Создаем связи (foreign keys)
        for table in tables:
            # Получаем foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            foreign_keys = cursor.fetchall()

            for fk in foreign_keys:
                # fk[2] - referenced table, fk[3] - referencing column, fk[4] - referenced column
                ref_table = fk[2]
                if ref_table in tables:
                    dot.edge(table, ref_table, label=f"{fk[3]}→{fk[4]}")

        conn.close()

        # Сохраняем диаграмму
        if tables:
            dot.render(output_file, cleanup=True)
            print(f"ER-диаграмма сохранена как: {output_file}.png")
        else:
            print("Нет таблиц для создания диаграммы")

    except Exception as e:
        print(f"Ошибка при создании диаграммы: {e}")
        import traceback
        traceback.print_exc()


def print_database_schema():
    """Вывод текстовой схемы базы данных"""

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        print("=" * 60)
        print("СХЕМА БАЗЫ ДАННЫХ")
        print("=" * 60)

        for table in tables:
            print(f"\nТАБЛИЦА: {table}")
            print("-" * 40)

            # Колонки
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            print("Колонки:")
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                constraints = []
                if pk:
                    constraints.append("PRIMARY KEY")
                if not_null:
                    constraints.append("NOT NULL")
                if default_val:
                    constraints.append(f"DEFAULT {default_val}")

                constraint_str = " " + " ".join(constraints) if constraints else ""
                print(f"  {col_name} {col_type}{constraint_str}")

            # Foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()

            if fks:
                print("Foreign Keys:")
                for fk in fks:
                    print(f"  {fk[3]} → {fk[2]}.{fk[4]}")

            # Индексы
            cursor.execute(f"PRAGMA index_list({table})")
            indexes = cursor.fetchall()

            if indexes:
                print("Индексы:")
                for idx in indexes:
                    if not idx[1].startswith('sqlite_'):  # Пропускаем системные индексы
                        print(f"  {idx[1]} ({'UNIQUE' if idx[2] else 'NON-UNIQUE'})")

        conn.close()

    except Exception as e:
        print(f"Ошибка: {e}")


def generate_simple_schema_diagram(output_file='simple_schema_diagram'):
    """Упрощенная диаграмма - только таблицы и связи"""

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Создаем граф
        dot = graphviz.Digraph(
            comment='Simple Schema Diagram',
            format='png',
            graph_attr={'rankdir': 'TB'}
        )

        # Получаем таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        # Добавляем узлы (просто названия таблиц)
        for table in tables:
            dot.node(table, shape='box', style='filled', fillcolor='lightblue')

        # Добавляем связи
        for table in tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()

            for fk in fks:
                ref_table = fk[2]
                if ref_table in tables:
                    dot.edge(table, ref_table)

        conn.close()

        # Сохраняем
        dot.render(output_file, cleanup=True)
        print(f"Упрощенная диаграмма сохранена как: {output_file}.png")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    # Сначала выводим текстовую схему
    print_database_schema()

    print("\n" + "=" * 60 + "\n")

    # Затем создаем подробную диаграмму
    generate_er_diagram_sqlite()

    print("\n" + "=" * 60 + "\n")

    # И упрощенную версию
    generate_simple_schema_diagram()
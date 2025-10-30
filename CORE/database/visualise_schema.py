from CORE.settings import DB_PATH
import os
import sqlite3
import graphviz


def generate_detailed_schema_diagram(output_file='database_er_diagram'):
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



def generate_er_diagram_group_colored_arrows(output_file='database_er_diagram_colored_arrows'):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        dot = graphviz.Digraph(
            comment='Database ER Diagram with Group-Colored Arrows',
            format='png',
            graph_attr={
                'rankdir': 'TB',
                'splines': 'spline',
                'overlap': 'false',
                'nodesep': '0.8',
                'ranksep': '1.2'
            }
        )

        # Группировка по вашему описанию
        groups = {
            'левые части объектов': {
                'tables': ['input_param_to_class', 'input_point_to_class', 'output_param_to_class',
                           'argument_to_class'],
                'color': 'lightcoral',
                'arrow_color': 'red'  # Цвет для стрелок из этой группы
            },
            'правые части объектов': {
                'tables': ['value_to_argument', 'value_to_input_param', 'value_to_input_point',
                           'value_to_output_param'],
                'color': 'lightgreen',
                'arrow_color': 'green'  # Цвет для стрелок из этой группы
            },
            'ядро базы': {
                'tables': ['point', 'parameter', 'form'],
                'color': 'lightblue',
                'arrow_color': 'blue'  # Цвет для стрелок из этой группы
            }
        }

        # Создаем кластеры для сгруппированных таблиц
        for group_name, group_info in groups.items():
            with dot.subgraph(name=f'cluster_{group_name}') as cluster:
                cluster.attr(
                    label=group_name,
                    style='filled,rounded',
                    fillcolor=group_info['color'],
                    color='black',
                    fontsize='12',
                    fontname='Arial'
                )

                for table in group_info['tables']:
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                    if cursor.fetchone():
                        cluster.node(
                            table,
                            shape='box',
                            style='filled',
                            fillcolor='white',
                            color='black'
                        )

        # Таблицы без группы (серые)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        all_tables = [row[0] for row in cursor.fetchall()]

        grouped_tables = []
        for group_info in groups.values():
            grouped_tables.extend(group_info['tables'])

        ungrouped_tables = [table for table in all_tables if table not in grouped_tables]

        # Добавляем несгруппированные таблицы
        with dot.subgraph(name='cluster_ungrouped') as cluster:
            cluster.attr(
                label='остальные таблицы',
                style='filled,rounded',
                fillcolor='lightgray',
                color='black',
                fontsize='12',
                fontname='Arial'
            )

            for table in ungrouped_tables:
                cluster.node(
                    table,
                    shape='box',
                    style='filled',
                    fillcolor='white',
                    color='black'
                )

        # Добавляем все связи между таблицами с цветами групп
        for table in all_tables:
            cursor.execute(f"PRAGMA foreign_key_list({table})")
            fks = cursor.fetchall()

            for fk in fks:
                ref_table = fk[2]
                if ref_table in all_tables:
                    # Определяем цвет стрелки на основе группы исходной таблицы
                    arrow_color = 'black'  # цвет по умолчанию для несгруппированных таблиц

                    # Проверяем только исходную таблицу (table), игнорируем целевую (ref_table)
                    for group_name, group_info in groups.items():
                        if table in group_info['tables']:
                            arrow_color = group_info['arrow_color']
                            break
                    # Если таблица в несгруппированных - оставляем черный цвет

                    dot.edge(
                        table,
                        ref_table,
                        color=arrow_color,
                        label=f"{fk[3]}→{fk[4]}",
                        arrowsize='0.8',
                        penwidth='1.2',
                        style='solid'
                    )

        conn.close()
        dot.render(output_file, cleanup=True)
        print(f"Диаграмма с цветными стрелками групп сохранена как: {output_file}.png")


    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()



if __name__ == "__main__":

    generate_detailed_schema_diagram()

    generate_simple_schema_diagram()

    generate_er_diagram_group_colored_arrows()


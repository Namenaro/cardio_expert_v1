import sqlite3

from CORE.paths import DB_PATH


def generate_html_report(output_file='REPORT.html'):
    """Генерация красивого HTML отчета по базе данных"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = [row[0] for row in cursor.fetchall()]

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Database Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .table-section { margin-bottom: 40px; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
                .table-name { background: #f0f0f0; padding: 10px; margin: -15px -15px 15px -15px; border-radius: 5px 5px 0 0; }
                table { width: 100%; border-collapse: collapse; }
                th { background: #4CAF50; color: white; padding: 10px; text-align: left; }
                td { padding: 8px; border-bottom: 1px solid #ddd; }
                tr:nth-child(even) { background: #f2f2f2; }
                tr:hover { background: #e9e9e9; }
            </style>
        </head>
        <body>
            <h1>📊 Отчет по базе данных</h1>
        """

        for table in tables:
            # Получаем структуру
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Получаем данные
            cursor.execute(f"SELECT * FROM {table} LIMIT 50")
            rows = cursor.fetchall()

            html_content += f"""
            <div class="table-section">
                <div class="table-name">
                    <h2>📋 Таблица: {table}</h2>
                    <p>Колонок: {len(columns)}, Строк: {len(rows)}</p>
                </div>
            """

            if rows:
                html_content += "<table>"
                html_content += "<tr>" + "".join(f"<th>{col}</th>" for col in column_names) + "</tr>"

                for row in rows:
                    html_content += "<tr>" + "".join(f"<td>{str(cell)}</td>" for cell in row) + "</tr>"

                html_content += "</table>"
            else:
                html_content += "<p>Таблица пуста</p>"

            html_content += "</div>"

        html_content += """
        </body>
        </html>
        """

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        conn.close()
        print(f"HTML отчет сохранен как: {output_file}")

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    generate_html_report()
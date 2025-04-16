import pyodbc

# Подключение к базе данных
DSN = 'Your_DSN'  # Укажи своё имя источника данных
conn = pyodbc.connect(f'DSN={DSN}')
cursor = conn.cursor()

# Получение всех таблиц
tables = [row.table_name for row in cursor.tables(tableType='TABLE')]

# Подсчёт строк в каждой таблице
table_sizes = []
for table in tables:
    try:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        table_sizes.append((table, count))
    except Exception as e:
        print(f'Ошибка при обработке таблицы {table}: {e}')

# Сортировка по размеру
table_sizes.sort(key=lambda x: x[1], reverse=True)

# Вывод топ-10 таблиц
print("Топ самых больших таблиц:")
for table, count in table_sizes[:10]:
    print(f"{table}: {count} строк")

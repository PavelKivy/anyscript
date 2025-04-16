import os
import csv
import pyodbc
import difflib
from datetime import datetime

# Настройки
DSN = 'Your_DSN'  # Заменить на имя источника данных
EXCLUDED_TABLES = {'samples', 'result'}
BACKUP_DIR = 'db_backups'

# Подключение
conn = pyodbc.connect(f'DSN={DSN}')
cursor = conn.cursor()

# Получение списка таблиц
def get_table_names():
    tables = []
    for row in cursor.tables(tableType='TABLE'):
        if row.table_name.lower() not in EXCLUDED_TABLES:
            tables.append(row.table_name)
    return tables

# Сохранение таблицы в CSV
def save_table_to_csv(table_name, dir_path):
    file_path = os.path.join(dir_path, f'{table_name}.csv')
    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [column[0] for column in cursor.description]
        writer.writerow(columns)
        for row in cursor.fetchall():
            writer.writerow(row)

# Сравнение файлов и вывод diff
def compare_files(file1, file2):
    with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
        f1_lines = f1.readlines()
        f2_lines = f2.readlines()
        diff = difflib.unified_diff(f1_lines, f2_lines, fromfile=file1, tofile=file2, lineterm='')
        for line in diff:
            print(line)

# Основная логика
def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if os.path.isdir(os.path.join(BACKUP_DIR, f))])
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_backup_path = os.path.join(BACKUP_DIR, timestamp)
    os.makedirs(new_backup_path)

    tables = get_table_names()
    for table in tables:
        save_table_to_csv(table, new_backup_path)

    if len(backups) >= 1:
        last_backup_path = os.path.join(BACKUP_DIR, backups[-1])
        print(f"\nИзменения по сравнению с бэкапом {backups[-1]}:\n")
        for table in tables:
            file1 = os.path.join(last_backup_path, f'{table}.csv')
            file2 = os.path.join(new_backup_path, f'{table}.csv')
            if os.path.exists(file1):
                compare_files(file1, file2)
            else:
                print(f"Файл {file1} отсутствует в предыдущем бэкапе.")

if __name__ == '__main__':
    main()

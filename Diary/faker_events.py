import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta

# Создаем соединение с базой данных
conn = sqlite3.connect('calendar.db')
cursor = conn.cursor()

# Создаем таблицу, если она не существует
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
''')

# Инициализируем Faker
fake = Faker()

# Функция для генерации случайной даты и времени
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# Генерируем 15 мероприятий
for _ in range(15):
    title = fake.sentence(nb_words=3)
    description = fake.text(max_nb_chars=200)
    event_date = random_date(datetime(2024, 9, 1), datetime(2025, 2, 15)).date()
    event_time = fake.time()  # Генерируем случайное время в формате HH:MM

    # Вставляем данные в таблицу
    cursor.execute('''
        INSERT INTO events (title, description, date, time)
        VALUES (?, ?, ?, ?)
    ''', (title, description, str(event_date), str(event_time)))

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()

print("База данных успешно заполнена 15 мероприятиями.")

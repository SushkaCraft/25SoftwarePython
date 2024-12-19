import sqlite3

conn = sqlite3.connect("shop.db")
c = conn.cursor()

categories = [
    "Электроника",
    "Одежда",
    "Книги",
    "Продукты питания",
    "Игрушки",
    "Косметика",
    "Спорттовары"
]

products = [
    {"name": "Смартфон", "price": 30000, "category": "Электроника", "stock": 10},
    {"name": "Ноутбук", "price": 70000, "category": "Электроника", "stock": 5},
    {"name": "Футболка", "price": 1500, "category": "Одежда", "stock": 50},
    {"name": "Джинсы", "price": 3500, "category": "Одежда", "stock": 30},
    {"name": "Роман '1984'", "price": 500, "category": "Книги", "stock": 100},
    {"name": "Учебник по Python", "price": 800, "category": "Книги", "stock": 40},
    {"name": "Хлеб", "price": 50, "category": "Продукты питания", "stock": 200},
    {"name": "Молоко", "price": 70, "category": "Продукты питания", "stock": 150},
    {"name": "Конструктор LEGO", "price": 4500, "category": "Игрушки", "stock": 20},
    {"name": "Плюшевый мишка", "price": 800, "category": "Игрушки", "stock": 25},
    {"name": "Крем для лица", "price": 1200, "category": "Косметика", "stock": 60},
    {"name": "Шампунь", "price": 600, "category": "Косметика", "stock": 80},
    {"name": "Футбольный мяч", "price": 2000, "category": "Спорттовары", "stock": 15},
    {"name": "Гантели", "price": 5000, "category": "Спорттовары", "stock": 10}
]

c.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    category_id INTEGER,
    stock INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
""")

c.execute("DELETE FROM products")
c.execute("DELETE FROM categories")
conn.commit()

category_ids = {}
for category in categories:
    c.execute("INSERT INTO categories (name) VALUES (?)", (category,))
    category_ids[category] = c.lastrowid
conn.commit()

for product in products:
    category_id = category_ids[product["category"]]
    c.execute("""
    INSERT INTO products (name, price, category_id, stock) VALUES (?, ?, ?, ?)
    """, (product["name"], product["price"], category_id, product["stock"]))
conn.commit()

print("Магазин успешно наполнен товарами.")

conn.close()

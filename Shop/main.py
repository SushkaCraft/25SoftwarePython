import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel

def create_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            stock INTEGER NOT NULL,
            category_id INTEGER,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            rating INTEGER,
            comment TEXT,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER,
            total_price REAL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_name TEXT,
            total_price REAL,
            order_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Магазин")
        self.root.geometry("1000x700")
        
        self.customer_name = None
        self.cart = []

        self.tab_control = ttk.Notebook(root)
        
        self.categories_tab = ttk.Frame(self.tab_control)
        self.cart_tab = ttk.Frame(self.tab_control)
        self.orders_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.categories_tab, text='Категории')
        self.tab_control.add(self.cart_tab, text='Корзина')
        self.tab_control.add(self.orders_tab, text='Заказы')
        
        self.tab_control.pack(expand=1, fill="both")

        self.create_categories_tab()
        self.create_cart_tab()
        self.create_orders_tab()

        self.prompt_customer_name()

    def create_categories_tab(self):
        self.categories_label = tk.Label(self.categories_tab, text="Выберите категорию товаров", font=("Arial", 16))
        self.categories_label.grid(row=0, column=0, padx=10, pady=10)

        self.load_categories()

    def load_categories(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT * FROM categories')
        categories = c.fetchall()
        conn.close()

        row = 1
        for category in categories:
            category_name = category[1]
            category_button = tk.Button(self.categories_tab, text=category_name, font=("Arial", 14),
                                        command=lambda category_id=category[0]: self.load_products_by_category(category_id))
            category_button.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            row += 1

    def load_products_by_category(self, category_id):
        self.products_window = Toplevel(self.root)
        self.products_window.title("Товары")
        self.products_window.geometry("600x400")

        self.products_label = tk.Label(self.products_window, text="Выберите товар", font=("Arial", 16))
        self.products_label.grid(row=0, column=0, padx=10, pady=10)

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('''
            SELECT p.id, p.name, p.price, p.description, p.stock 
            FROM products p 
            WHERE p.category_id = ?
        ''', (category_id,))
        products = c.fetchall()
        conn.close()

        row = 1
        for product in products:
            product_button = tk.Button(self.products_window, text=product[1], font=("Arial", 14),
                                       command=lambda product_id=product[0]: self.show_product_details(product_id))
            product_button.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            row += 1

    def show_product_details(self, product_id):
        self.product_window = Toplevel(self.root)
        self.product_window.title("Информация о товаре")
        self.product_window.geometry("600x400")

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('''
            SELECT p.id, p.name, p.price, p.description, p.stock, c.name 
            FROM products p 
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        ''', (product_id,))
        product = c.fetchone()

        conn.close()

        product_name, price, description, stock, category = product[1], product[2], product[3], product[4], product[5]

        self.product_name_label = tk.Label(self.product_window, text=f"Название: {product_name}", font=("Arial", 16))
        self.product_name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.product_category_label = tk.Label(self.product_window, text=f"Категория: {category}", font=("Arial", 14))
        self.product_category_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.product_price_label = tk.Label(self.product_window, text=f"Цена: {price} руб.", font=("Arial", 14))
        self.product_price_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.product_description_label = tk.Label(self.product_window, text=f"Описание: {description}", font=("Arial", 14))
        self.product_description_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.product_stock_label = tk.Label(self.product_window, text=f"Наличие: {stock} шт.", font=("Arial", 14))
        self.product_stock_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")

        self.add_to_cart_button = tk.Button(self.product_window, text="Добавить в корзину", font=("Arial", 14),
                                            command=lambda: self.add_to_cart(product_id, product_name, price, stock))
        self.add_to_cart_button.grid(row=5, column=0, padx=10, pady=10)

        self.view_reviews_button = tk.Button(self.product_window, text="Посмотреть отзывы", font=("Arial", 14),
                                             command=lambda: self.show_reviews(product_id))
        self.view_reviews_button.grid(row=6, column=0, padx=10, pady=5)

    def create_cart_tab(self):
        self.cart_label = tk.Label(self.cart_tab, text="Ваша корзина пуста", font=("Arial", 16))
        self.cart_label.grid(row=0, column=0, padx=10, pady=10)

    def add_to_cart(self, product_id, product_name, price, stock):
        quantity = 1
        
        if stock > 0:
            total_price = price * quantity
            self.cart.append((product_id, product_name, price, quantity, total_price))

            self.load_cart()
            messagebox.showinfo("Успех", "Товар добавлен в корзину!")
        else:
            messagebox.showwarning("Ошибка", "Товара нет в наличии!")

    def create_orders_tab(self):
        self.orders_label = tk.Label(self.orders_tab, text="Ваши заказы", font=("Arial", 16))
        self.orders_label.grid(row=0, column=0, padx=10, pady=10)

        self.load_orders()

    def load_orders(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM orders")
        orders = c.fetchall()
        conn.close()

        row = 1
        for order in orders:
            order_label = tk.Label(self.orders_tab, text=f"Заказ #{order[0]} - {order[1]} - {order[2]} руб.", font=("Arial", 14))
            order_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            row += 1

    def load_cart(self):
        for widget in self.cart_tab.winfo_children():
            widget.destroy()

        self.cart_label = tk.Label(self.cart_tab, text="Ваша корзина", font=("Arial", 16))
        self.cart_label.grid(row=0, column=0, padx=10, pady=10)

        row = 1
        total_price = 0
        for item in self.cart:
            product_name, price, quantity, total = item[1], item[2], item[3], item[4]
            total_price += total
            cart_item_label = tk.Label(self.cart_tab, text=f"{product_name} - {quantity} шт. - {total} руб.", font=("Arial", 14))
            cart_item_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            row += 1

        self.total_price_label = tk.Label(self.cart_tab, text=f"Общая сумма: {total_price} руб.", font=("Arial", 16))
        self.total_price_label.grid(row=row, column=0, padx=10, pady=10)

        self.checkout_button = tk.Button(self.cart_tab, text="Оформить заказ", font=("Arial", 14), command=self.checkout)
        self.checkout_button.grid(row=row+1, column=0, padx=10, pady=10)

    def checkout(self):
        if not self.cart:
            messagebox.showwarning("Корзина пуста", "Добавьте товары в корзину перед оформлением заказа.")
            return

        self.checkout_window = Toplevel(self.root)
        self.checkout_window.title("Оформление заказа")
        self.checkout_window.geometry("300x200")

        self.checkout_label = tk.Label(self.checkout_window, text="Введите ваше имя:", font=("Arial", 14))
        self.checkout_label.pack(pady=10)

        self.name_entry = tk.Entry(self.checkout_window, font=("Arial", 14))
        self.name_entry.pack(pady=5)

        self.submit_button = tk.Button(self.checkout_window, text="Оформить заказ", font=("Arial", 14), command=self.place_order)
        self.submit_button.pack(pady=10)

    def place_order(self):
        customer_name = self.name_entry.get()

        if not customer_name:
            messagebox.showwarning("Ошибка", "Введите имя клиента.")
            return

        total_price = sum(item[4] for item in self.cart)

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute("INSERT INTO orders (customer_name, total_price, order_date) VALUES (?, ?, DATE('now'))",
                  (customer_name, total_price))
        order_id = c.lastrowid

        for item in self.cart:
            product_id, product_name, price, quantity, total = item
            c.execute("INSERT INTO cart (product_id, quantity, total_price) VALUES (?, ?, ?)",
                      (product_id, quantity, total))

        conn.commit()
        conn.close()

        self.cart.clear()
        self.load_cart()
        self.load_orders()
        
        messagebox.showinfo("Успех", "Заказ успешно оформлен!")

    def prompt_customer_name(self):
        self.name_window = tk.Toplevel(self.root)
        self.name_window.title("Введите имя")
        self.name_window.geometry("300x150")

        self.name_label = tk.Label(self.name_window, text="Введите ваше имя:")
        self.name_label.pack(pady=10)

        self.name_entry = tk.Entry(self.name_window)
        self.name_entry.pack(pady=5)

        self.submit_button = tk.Button(self.name_window, text="Подтвердить", command=self.set_customer_name)
        self.submit_button.pack(pady=10)

    def set_customer_name(self):
        self.customer_name = self.name_entry.get()
        self.name_window.destroy()


if __name__ == "__main__":
    create_db()
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

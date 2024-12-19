import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def create_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

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
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')

    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'Admin')")
    
    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Административная панель магазина")
        self.root.geometry("1000x700")
        
        self.role = "Admin"
        self.customer_name = "Admin"

        self.tab_control = ttk.Notebook(root)
        
        self.categories_tab = ttk.Frame(self.tab_control)
        self.cart_tab = ttk.Frame(self.tab_control)
        self.orders_tab = ttk.Frame(self.tab_control)
        self.stats_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.categories_tab, text='Категории')
        self.tab_control.add(self.cart_tab, text='Корзина')
        self.tab_control.add(self.orders_tab, text='Заказы')
        self.tab_control.add(self.stats_tab, text='Статистика')
        
        self.tab_control.pack(expand=1, fill="both")

        self.create_categories_tab()
        self.create_cart_tab()
        self.create_orders_tab()
        self.create_stats_tab()

        self.check_admin()

    def checkout(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        
        c.execute('SELECT SUM(total_price) FROM cart')
        total_price = c.fetchone()[0] or 0
        
        if total_price <= 0:
            messagebox.showerror("Ошибка", "Корзина пуста или сумма заказа некорректна.")
            return

        from datetime import datetime
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        c.execute('''INSERT INTO orders (customer_name, total_price, order_date) VALUES (?, ?, ?)''', 
                (self.customer_name, total_price, order_date))
        order_id = c.lastrowid
        conn.commit()
        c.execute('SELECT product_id, quantity FROM cart')
        cart_items = c.fetchall()
        for item in cart_items:
            c.execute('''INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)''', 
                    (order_id, item[0], item[1]))
        
        conn.commit()
        conn.close()

        self.clear_cart()
        messagebox.showinfo("Успех", "Ваш заказ оформлен!")

        self.create_stats_tab()

    def check_admin(self):
        if self.role == "Admin":
            self.create_admin_controls()

    def create_admin_controls(self):
        self.edit_product_button = tk.Button(self.categories_tab, text="Редактировать товары", font=("Arial", 14), command=self.edit_product)
        self.edit_product_button.grid(row=1, column=0, padx=10, pady=10)

        self.edit_order_button = tk.Button(self.orders_tab, text="Редактировать заказы", font=("Arial", 14), command=self.edit_order)
        self.edit_order_button.grid(row=1, column=0, padx=10, pady=10)

        self.add_product_button = tk.Button(self.categories_tab, text="Добавить товар", font=("Arial", 14), command=self.add_product)
        self.add_product_button.grid(row=2, column=0, padx=10, pady=10)

        self.view_orders_button = tk.Button(self.orders_tab, text="Просмотр заказов", font=("Arial", 14), command=self.view_orders)
        self.view_orders_button.grid(row=2, column=0, padx=10, pady=10)

    def create_categories_tab(self):
        self.category_label = tk.Label(self.categories_tab, text="Категории товаров", font=("Arial", 18))
        self.category_label.grid(row=0, column=0, padx=10, pady=10)

    def create_cart_tab(self):
        self.cart_label = tk.Label(self.cart_tab, text="Корзина покупок", font=("Arial", 18))
        self.cart_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.product_listbox = tk.Listbox(self.cart_tab, width=50, height=10)
        self.product_listbox.grid(row=1, column=0, padx=10, pady=10)

        self.load_products_for_cart()
        
        self.add_to_cart_button = tk.Button(self.cart_tab, text="Добавить в корзину", font=("Arial", 14), command=self.add_to_cart)
        self.add_to_cart_button.grid(row=2, column=0, padx=10, pady=10)

        self.cart_listbox = tk.Listbox(self.cart_tab, width=50, height=10)
        self.cart_listbox.grid(row=3, column=0, padx=10, pady=10)

        self.checkout_button = tk.Button(self.cart_tab, text="Оформить заказ", font=("Arial", 14), command=self.checkout)
        self.checkout_button.grid(row=4, column=0, padx=10, pady=10)

    def load_products_for_cart(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT id, name, price, stock FROM products')
        products = c.fetchall()
        conn.close()

        self.product_listbox.delete(0, tk.END)
        for product in products:
            self.product_listbox.insert(tk.END, f"ID: {product[0]} - {product[1]} - Цена: {product[2]} - В наличии: {product[3]}")

    def add_to_cart(self):
        selected_product = self.product_listbox.curselection()
        print("selected_product:", selected_product)
        if not selected_product:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите товар.")
            return
            
        product_info = self.product_listbox.get(selected_product[0]).split(" - ")

        if len(product_info) <= 3:
            messagebox.showerror("Ошибка", "Некорректный формат информации о товаре.")
            return
        
        try:
            product_id = int(product_info[0].split(":")[1].strip())
            product_name = product_info[1].strip()
            product_price = float(product_info[2].split(":")[1].strip())
            product_stock = int(product_info[3].split(":")[1].strip()) 
            
        except IndexError as e:
            messagebox.showerror("Ошибка", "Не удалось извлечь данные о товаре. Ошибка: " + str(e))
            return
        except ValueError as e:
            messagebox.showerror("Ошибка", "Ошибка преобразования данных: " + str(e))
            return
            
        quantity = self.ask_quantity()

        if quantity:
            total_price = product_price * quantity
            try:
                conn = sqlite3.connect('shop.db')
                c = conn.cursor()
                c.execute('''INSERT INTO cart (product_id, quantity, total_price) VALUES (?, ?, ?)''', 
                        (product_id, quantity, total_price))
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                messagebox.showerror("Ошибка базы данных", "Не удалось добавить товар в корзину. Ошибка: " + str(e))
                
            self.update_cart_display()
            messagebox.showinfo("Успех", f"Товар '{product_name}' добавлен в корзину.")

    def create_orders_tab(self):
        self.orders_label = tk.Label(self.orders_tab, text="Заказы", font=("Arial", 18))
        self.orders_label.grid(row=0, column=0, padx=10, pady=10)

    def create_stats_tab(self):
        for widget in self.stats_tab.winfo_children():
            widget.destroy()
        self.stats_label = tk.Label(self.stats_tab, text="Статистика магазина", font=("Arial", 18))
        self.stats_label.grid(row=0, column=0, padx=10, pady=10)
        self.plot_product_selection()
        self.plot_order_statistics()

    def plot_product_selection(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        
        c.execute('''SELECT products.name, SUM(order_items.quantity) 
             FROM order_items 
             JOIN products ON order_items.product_id = products.id 
             GROUP BY products.name''')
        data = c.fetchall()
        conn.close()

        if not data:
            tk.Label(self.stats_tab, text="Нет данных для отображения статистики", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
            return

        product_names = [item[0] for item in data]
        quantities = [item[1] for item in data]

        total_orders = sum(quantities)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(
            quantities, 
            labels=[f"{name} ({q} шт)" for name, q in zip(product_names, quantities)], 
            autopct=lambda p: f'{p:.1f}%\n({int(p * total_orders / 100)} шт)',
            startangle=140,
            wedgeprops={'edgecolor': 'white'}
        )
        ax.set_title('Соотношение количества товаров в заказах')

        canvas = FigureCanvasTkAgg(fig, master=self.stats_tab)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)


    def plot_order_statistics(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()

        c.execute('''SELECT strftime('%Y-%m', order_date) AS month, COUNT(*) 
                    FROM orders 
                    GROUP BY month 
                    ORDER BY month''')
        data = c.fetchall()
        conn.close()

        months = [item[0] for item in data]
        order_counts = [item[1] for item in data]

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(months, order_counts, marker='o', linestyle='-', color='green')
        ax.set_xlabel('Месяцы')
        ax.set_ylabel('Количество заказов')
        ax.set_title('Частота заказов по месяцам')

        canvas = FigureCanvasTkAgg(fig, master=self.stats_tab)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0, padx=10, pady=10)

    def clear_cart(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('DELETE FROM cart')
        conn.commit()
        conn.close()
        self.update_cart_display()

    def update_cart_display(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT products.name, cart.quantity, cart.total_price FROM cart JOIN products ON cart.product_id = products.id')
        cart_items = c.fetchall()
        conn.close()
        
        self.cart_listbox.delete(0, tk.END)
        for item in cart_items:
            self.cart_listbox.insert(tk.END, f"{item[0]} - Количество: {item[1]} - Общая стоимость: {item[2]}")

    def ask_quantity(self):
        quantity_window = Toplevel(self.root)
        quantity_window.title("Введите количество")
        
        quantity_label = tk.Label(quantity_window, text="Количество товара:")
        quantity_label.pack(padx=10, pady=10)
        
        quantity_entry = tk.Entry(quantity_window)
        quantity_entry.pack(padx=10, pady=10)
        
        def submit_quantity():
            quantity = quantity_entry.get()
            try:
                quantity = int(quantity)
                quantity_window.destroy()
                self.add_to_cart_with_quantity(quantity)
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректное количество.")

        submit_button = tk.Button(quantity_window, text="Подтвердить", command=submit_quantity)
        submit_button.pack(padx=10, pady=10)

    def add_to_cart_with_quantity(self, quantity):
        selected_product = self.product_listbox.curselection()
        if not selected_product:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите товар.")
            return

        product_info = self.product_listbox.get(selected_product[0]).split(" - ")
        
        try:
            product_id = int(product_info[0].split(":")[1].strip())
            product_price = float(product_info[2].split(":")[1].strip())
        except (IndexError, ValueError):
            messagebox.showerror("Ошибка", "Некорректная информация о товаре.")
            return
        
        total_price = product_price * quantity
        
        try:
            conn = sqlite3.connect('shop.db')
            c = conn.cursor()
            c.execute('''INSERT INTO cart (product_id, quantity, total_price) VALUES (?, ?, ?)''', 
                    (product_id, quantity, total_price))
            conn.commit()
            conn.close()
            self.update_cart_display()
            messagebox.showinfo("Успех", "Товар добавлен в корзину.")
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Не удалось добавить товар в корзину. Ошибка: {e}")

    def edit_product(self):
        self.edit_product_window = Toplevel(self.root)
        self.edit_product_window.title("Редактировать товар")
        self.edit_product_window.geometry("400x300")
        
        self.load_product_edit()

    def load_product_edit(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT id, name, price, stock FROM products')
        products = c.fetchall()
        conn.close()

        self.product_listbox = tk.Listbox(self.edit_product_window, width=50, height=10)
        self.product_listbox.pack(padx=10, pady=10)

        for product in products:
            self.product_listbox.insert(tk.END, f"ID: {product[0]} - {product[1]} - Цена: {product[2]} - В наличии: {product[3]}")

        self.edit_button = tk.Button(self.edit_product_window, text="Изменить", font=("Arial", 14), command=self.update_product)
        self.edit_button.pack(pady=10)

    def update_product(self):
        selected_product = self.product_listbox.curselection()
        if selected_product:
            product_id = selected_product[0] + 1
            self.edit_product_form(product_id)

    def edit_product_form(self, product_id):
        self.product_form_window = Toplevel(self.root)
        self.product_form_window.title("Редактирование товара")
        self.product_form_window.geometry("400x300")

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        product = c.fetchone()
        conn.close()

        self.product_name_label = tk.Label(self.product_form_window, text="Название товара:")
        self.product_name_label.pack(pady=5)
        self.product_name_entry = tk.Entry(self.product_form_window)
        self.product_name_entry.insert(0, product[1])
        self.product_name_entry.pack(pady=5)

        self.product_price_label = tk.Label(self.product_form_window, text="Цена товара:")
        self.product_price_label.pack(pady=5)
        self.product_price_entry = tk.Entry(self.product_form_window)
        self.product_price_entry.insert(0, str(product[2]))
        self.product_price_entry.pack(pady=5)

        self.product_stock_label = tk.Label(self.product_form_window, text="Количество товара:")
        self.product_stock_label.pack(pady=5)
        self.product_stock_entry = tk.Entry(self.product_form_window)
        self.product_stock_entry.insert(0, str(product[4]))
        self.product_stock_entry.pack(pady=5)

        self.update_product_button = tk.Button(self.product_form_window, text="Сохранить изменения", font=("Arial", 14), command=lambda: self.save_product_changes(product_id))
        self.update_product_button.pack(pady=10)

    def save_product_changes(self, product_id):
        new_name = self.product_name_entry.get()
        new_price = float(self.product_price_entry.get())
        new_stock = int(self.product_stock_entry.get())

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('''
            UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?
        ''', (new_name, new_price, new_stock, product_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Информация о товаре обновлена!")
        self.edit_product_window.destroy()

    def add_product(self):
        self.add_product_window = Toplevel(self.root)
        self.add_product_window.title("Добавить товар")
        self.add_product_window.geometry("400x300")

        self.product_name_label = tk.Label(self.add_product_window, text="Название товара:")
        self.product_name_label.pack(pady=5)
        self.product_name_entry = tk.Entry(self.add_product_window)
        self.product_name_entry.pack(pady=5)

        self.product_price_label = tk.Label(self.add_product_window, text="Цена товара:")
        self.product_price_label.pack(pady=5)
        self.product_price_entry = tk.Entry(self.add_product_window)
        self.product_price_entry.pack(pady=5)

        self.product_stock_label = tk.Label(self.add_product_window, text="Количество товара:")
        self.product_stock_label.pack(pady=5)
        self.product_stock_entry = tk.Entry(self.add_product_window)
        self.product_stock_entry.pack(pady=5)

        self.add_button = tk.Button(self.add_product_window, text="Добавить товар", font=("Arial", 14), command=self.save_new_product)
        self.add_button.pack(pady=10)

    def save_new_product(self):
        new_name = self.product_name_entry.get()
        new_price = float(self.product_price_entry.get())
        new_stock = int(self.product_stock_entry.get())

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO products (name, price, stock) VALUES (?, ?, ?)
        ''', (new_name, new_price, new_stock))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Товар добавлен!")
        self.add_product_window.destroy()

    def view_orders(self):
        self.view_orders_window = Toplevel(self.root)
        self.view_orders_window.title("Просмотр заказов")
        self.view_orders_window.geometry("500x400")
        
        self.load_orders()

    def edit_order(self):
        self.edit_order_window = Toplevel(self.root)
        self.edit_order_window.title("Редактировать заказ")
        self.edit_order_window.geometry("400x300")
        
        self.load_order_edit()

    def load_order_edit(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT id, customer_name, total_price, order_date FROM orders')
        orders = c.fetchall()
        conn.close()

        self.order_listbox = tk.Listbox(self.edit_order_window, width=50, height=10)
        self.order_listbox.pack(padx=10, pady=10)

        for order in orders:
            self.order_listbox.insert(tk.END, f"ID: {order[0]} - {order[1]} - Сумма: {order[2]} - Дата: {order[3]}")

        self.edit_order_button = tk.Button(self.edit_order_window, text="Изменить", font=("Arial", 14), command=self.update_order)
        self.edit_order_button.pack(pady=10)

    def load_orders(self):
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT id, customer_name, total_price, order_date FROM orders')
        orders = c.fetchall()
        conn.close()

        self.orders_listbox = tk.Listbox(self.view_orders_window, width=60, height=10)
        self.orders_listbox.pack(padx=10, pady=10)

        for order in orders:
            self.orders_listbox.insert(tk.END, f"ID: {order[0]} - {order[1]} - Сумма: {order[2]} - Дата: {order[3]}")

    def update_order(self):
        selected_order = self.order_listbox.curselection()
        if selected_order:
            order_id = selected_order[0] + 1
            self.edit_order_form(order_id)

    def edit_order_form(self, order_id):
        self.order_form_window = Toplevel(self.root)
        self.order_form_window.title("Редактирование заказа")
        self.order_form_window.geometry("400x300")

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        order = c.fetchone()
        conn.close()

        self.order_customer_label = tk.Label(self.order_form_window, text="Имя клиента:")
        self.order_customer_label.pack(pady=5)
        self.order_customer_entry = tk.Entry(self.order_form_window)
        self.order_customer_entry.insert(0, order[1])
        self.order_customer_entry.pack(pady=5)

        self.order_total_label = tk.Label(self.order_form_window, text="Сумма заказа:")
        self.order_total_label.pack(pady=5)
        self.order_total_entry = tk.Entry(self.order_form_window)
        self.order_total_entry.insert(0, str(order[2]))
        self.order_total_entry.pack(pady=5)

        self.update_order_button = tk.Button(self.order_form_window, text="Сохранить изменения", font=("Arial", 14), command=lambda: self.save_order_changes(order_id))
        self.update_order_button.pack(pady=10)

    def save_order_changes(self, order_id):
        new_customer_name = self.order_customer_entry.get()
        new_total_price = float(self.order_total_entry.get())

        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute('''
            UPDATE orders SET customer_name = ?, total_price = ? WHERE id = ?
        ''', (new_customer_name, new_total_price, order_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Информация о заказе обновлена!")
        self.edit_order_window.destroy()

if __name__ == "__main__":
    create_db()
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

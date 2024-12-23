import sqlite3
import tkinter as tk
from tkinter import ttk

def create_db():
    conn = sqlite3.connect('school_lunch.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            menu_item_id INTEGER,
            quantity INTEGER,
            order_date TEXT,
            FOREIGN KEY (menu_item_id) REFERENCES menu(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY,
            menu_item_id INTEGER,
            total_orders INTEGER,
            FOREIGN KEY (menu_item_id) REFERENCES menu(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY,
            meal_time TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            UNIQUE(meal_time, start_time)
        )
    ''')
    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Автоматизация школьного питания")
        self.root.geometry("800x460")
        
        self.tab_control = ttk.Notebook(root)
        
        self.menu_tab = ttk.Frame(self.tab_control)
        self.orders_tab = ttk.Frame(self.tab_control)
        self.statistics_tab = ttk.Frame(self.tab_control)
        self.add_item_tab = ttk.Frame(self.tab_control)
        self.schedule_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.menu_tab, text='Меню')
        self.tab_control.add(self.orders_tab, text='Заказы')
        self.tab_control.add(self.statistics_tab, text='Статистика')
        self.tab_control.add(self.add_item_tab, text='Добавить Блюдо')
        self.tab_control.add(self.schedule_tab, text='Расписание')
        
        self.tab_control.pack(expand=1, fill="both")

        self.create_menu_tab()
        self.create_orders_tab()
        self.create_statistics_tab()
        self.create_add_item_tab()
        self.create_schedule_tab()

    def create_menu_tab(self):
        self.menu_treeview = ttk.Treeview(self.menu_tab, columns=("ID", "Название", "Цена", "Описание"), show="headings")
        self.menu_treeview.heading("ID", text="ID")
        self.menu_treeview.heading("Название", text="Название")
        self.menu_treeview.heading("Цена", text="Цена")
        self.menu_treeview.heading("Описание", text="Описание")
        self.menu_treeview.pack(fill="both", expand=True, pady=10)

        self.load_menu()

    def create_orders_tab(self):
        self.orders_label = tk.Label(self.orders_tab, text="Выберите блюдо и укажите количество:")
        self.orders_label.grid(row=0, column=0, padx=10, pady=10)

        self.orders_treeview = ttk.Treeview(self.orders_tab, columns=("Меню", "Количество", "Дата заказа"), show="headings")
        self.orders_treeview.heading("Меню", text="Меню")
        self.orders_treeview.heading("Количество", text="Количество")
        self.orders_treeview.heading("Дата заказа", text="Дата заказа")
        self.orders_treeview.grid(row=1, column=0, padx=10, pady=10)

        self.quantity_label = tk.Label(self.orders_tab, text="Количество:")
        self.quantity_label.grid(row=2, column=0, padx=10, pady=5)

        self.quantity_entry = tk.Entry(self.orders_tab)
        self.quantity_entry.grid(row=3, column=0, padx=10, pady=5)

        self.order_button = tk.Button(self.orders_tab, text="Сделать заказ", command=self.place_order)
        self.order_button.grid(row=4, column=0, padx=10, pady=10)

        self.load_menu_for_orders()

    def create_statistics_tab(self):
        self.statistics_treeview = ttk.Treeview(self.statistics_tab, columns=("Меню", "Общее количество заказов"), show="headings")
        self.statistics_treeview.heading("Меню", text="Меню")
        self.statistics_treeview.heading("Общее количество заказов", text="Общее количество заказов")
        self.statistics_treeview.grid(row=0, column=0, padx=10, pady=10)

        self.load_statistics()

    def create_add_item_tab(self):
        self.name_label = tk.Label(self.add_item_tab, text="Название блюда:")
        self.name_label.grid(row=0, column=0, padx=10, pady=10)

        self.name_entry = tk.Entry(self.add_item_tab)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.price_label = tk.Label(self.add_item_tab, text="Цена блюда:")
        self.price_label.grid(row=1, column=0, padx=10, pady=10)

        self.price_entry = tk.Entry(self.add_item_tab)
        self.price_entry.grid(row=1, column=1, padx=10, pady=10)

        self.description_label = tk.Label(self.add_item_tab, text="Описание блюда:")
        self.description_label.grid(row=2, column=0, padx=10, pady=10)

        self.description_entry = tk.Entry(self.add_item_tab)
        self.description_entry.grid(row=2, column=1, padx=10, pady=10)

        self.add_button = tk.Button(self.add_item_tab, text="Добавить блюдо", command=self.add_item)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)

    def create_schedule_tab(self):
        self.schedule_treeview = ttk.Treeview(self.schedule_tab, columns=("Прием пищи", "Время начала", "Время окончания"), show="headings")
        self.schedule_treeview.heading("Прием пищи", text="Прием пищи")
        self.schedule_treeview.heading("Время начала", text="Время начала")
        self.schedule_treeview.heading("Время окончания", text="Время окончания")
        self.schedule_treeview.grid(row=0, column=0, padx=10, pady=10)

        self.load_schedule()

    def load_menu(self):
        conn = sqlite3.connect('school_lunch.db')
        c = conn.cursor()
        c.execute("SELECT id, name, price, description FROM menu")
        menu_items = c.fetchall()
        conn.close()
        
        self.menu_treeview.delete(*self.menu_treeview.get_children())
        for item in menu_items:
            self.menu_treeview.insert("", tk.END, values=item)

    def load_menu_for_orders(self):
        conn = sqlite3.connect('school_lunch.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM menu")
        menu_items = c.fetchall()
        conn.close()
        
        self.orders_treeview.delete(*self.orders_treeview.get_children())
        for item in menu_items:
            self.orders_treeview.insert("", tk.END, values=(item[1], "", ""))

    def load_statistics(self):
        conn = sqlite3.connect('school_lunch.db')
        c = conn.cursor()
        c.execute('''SELECT menu.name, SUM(orders.quantity)
                     FROM orders
                     JOIN menu ON orders.menu_item_id = menu.id
                     GROUP BY menu.id''')
        stats = c.fetchall()
        conn.close()

        self.statistics_treeview.delete(*self.statistics_treeview.get_children())
        for stat in stats:
            self.statistics_treeview.insert("", tk.END, values=stat)

    def load_schedule(self):
        conn = sqlite3.connect('school_lunch.db')
        c = conn.cursor()
        c.execute("SELECT meal_time, start_time, end_time FROM schedule")
        schedule_items = c.fetchall()
        conn.close()

        self.schedule_treeview.delete(*self.schedule_treeview.get_children())
        for item in schedule_items:
            self.schedule_treeview.insert("", tk.END, values=item)

    def place_order(self):
        selected_item = self.orders_treeview.selection()
        if selected_item:
            item_name = self.orders_treeview.item(selected_item[0])["values"][0]
            quantity = self.quantity_entry.get()

            if quantity.isdigit():
                conn = sqlite3.connect('school_lunch.db')
                c = conn.cursor()
                c.execute("SELECT id FROM menu WHERE name=?", (item_name,))
                menu_item_id = c.fetchone()[0]
                c.execute("INSERT INTO orders (menu_item_id, quantity, order_date) VALUES (?, ?, DATE('now'))",
                          (menu_item_id, int(quantity)))
                conn.commit()
                conn.close()

                self.load_statistics()
                self.quantity_entry.delete(0, tk.END)
            else:
                print("Введите корректное количество!")

    def add_item(self):
        name = self.name_entry.get()
        price = self.price_entry.get()
        description = self.description_entry.get()

        if name and price and description:
            conn = sqlite3.connect('school_lunch.db')
            c = conn.cursor()
            c.execute("INSERT INTO menu (name, price, description) VALUES (?, ?, ?)", (name, float(price), description))
            conn.commit()
            conn.close()

            self.load_menu_for_orders()
            self.load_menu()
            self.name_entry.delete(0, tk.END)
            self.price_entry.delete(0, tk.END)
            self.description_entry.delete(0, tk.END)

if __name__ == "__main__":
    create_db()
    conn = sqlite3.connect('school_lunch.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO schedule (meal_time, start_time, end_time) VALUES ('Завтрак', '08:00', '09:00')")
    c.execute("INSERT OR IGNORE INTO schedule (meal_time, start_time, end_time) VALUES ('Обед', '12:00', '13:00')")
    c.execute("INSERT OR IGNORE INTO schedule (meal_time, start_time, end_time) VALUES ('Ужин', '18:00', '19:00')")
    conn.commit()
    conn.close()
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

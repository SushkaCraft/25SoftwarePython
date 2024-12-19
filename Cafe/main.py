import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_and_fill_db():
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    price REAL,
                    stock INTEGER,
                    category TEXT)''')
    
    c.execute("DELETE FROM products WHERE stock = 0")

    products = [
        ("Суп куриный", 200, 10, "Блюда"),
        ("Паста карбонара", 350, 8, "Блюда"),
        ("Пицца маргарита", 400, 6, "Блюда"),
        ("Чай черный", 50, 20, "Напитки"),
        ("Кофе американо", 100, 15, "Напитки"),
        ("Лимонад", 150, 12, "Напитки"),
        ("Чизкейк", 250, 8, "Десерты"),
        ("Тирамису", 300, 5, "Десерты"),
        ("Картофель фри", 150, 10, "Закуски"),
        ("Наггетсы", 180, 7, "Закуски"),
        ("Сэндвич с курицей", 200, 9, "Закуски"),
        ("Суп грибной", 220, 15, "Блюда"),
        ("Паста болоньезе", 350, 10, "Блюда"),
        ("Пицца пепперони", 450, 5, "Блюда"),
        ("Коктейль молочный", 120, 18, "Напитки"),
        ("Кофе латте", 150, 13, "Напитки"),
        ("Фреш апельсиновый", 180, 10, "Напитки"),
        ("Шоколадный торт", 300, 6, "Десерты"),
        ("Морозное суфле", 350, 4, "Десерты"),
        ("Панини с ветчиной", 220, 8, "Закуски"),
        ("Салат \"Цезарь\"", 300, 10, "Закуски"),
        ("Крокеты с сыром", 180, 9, "Закуски"),
        ("Пельмени домашние", 280, 12, "Блюда"),
        ("Паста с морепродуктами", 400, 6, "Блюда"),
        ("Пицца с грибами", 380, 7, "Блюда"),
        ("Кофе капучино", 170, 16, "Напитки"),
        ("Сок яблочный", 130, 25, "Напитки"),
        ("Лимонад с мятой", 160, 14, "Напитки"),
        ("Торт \"Наполеон\"", 280, 8, "Десерты"),
        ("Карамельный пудинг", 250, 9, "Десерты"),
        ("Фрукты (ассорти)", 200, 15, "Десерты"),
        ("Греческий салат", 280, 10, "Закуски"),
        ("Роллы с лососем", 350, 7, "Закуски"),
        ("Сэндвич с тунцом", 250, 9, "Закуски"),
        ("Говядина с картошкой", 450, 5, "Блюда"),
        ("Пельмени с курицей", 300, 10, "Блюда"),
        ("Чизбургер", 220, 13, "Закуски"),
        ("Куриные крылышки", 230, 12, "Закуски"),
        ("Салат с тунцом", 320, 8, "Закуски"),
        ("Ризотто с грибами", 400, 5, "Блюда"),
        ("Фахитас с курицей", 350, 6, "Блюда"),
        ("Гриль-сэндвич с сыром", 200, 10, "Закуски"),
        ("Торт \"Медовик\"", 270, 7, "Десерты"),
        ("Крем-брюле", 280, 6, "Десерты"),
        ("Пирог с ягодами", 250, 9, "Десерты"),
        ("Котлеты по-киевски", 350, 6, "Блюда")
    ]
    for product in products:
        c.execute("SELECT * FROM products WHERE name = ?", (product[0],))
        existing_product = c.fetchone()
        if not existing_product:
            c.execute("INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)", product)
    conn.commit()
    conn.close()

class CafeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Автономное кафе")
        self.root.geometry("1280x640")
        
        self.notebook = ttk.Notebook(root)
        self.menu_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.statistics_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.menu_tab, text="Меню заказов")
        self.notebook.add(self.inventory_tab, text="Инвентарь")
        self.notebook.add(self.statistics_tab, text="Статистика")
        self.notebook.pack(expand=1, fill="both", padx=10, pady=10)
        
        self.create_order_tab()
        self.create_inventory_tab()
        self.create_statistics_tab()

    def create_order_tab(self):
        ttk.Label(self.menu_tab, text="Выберите категорию:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.category_combobox = ttk.Combobox(self.menu_tab, values=["Блюда", "Напитки", "Закуски", "Десерты"])
        self.category_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.category_combobox.bind("<<ComboboxSelected>>", self.load_products)

        ttk.Label(self.menu_tab, text="Выберите товар:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.product_combobox = ttk.Combobox(self.menu_tab)
        self.product_combobox.grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(self.menu_tab, text="Количество:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.quantity_entry = ttk.Entry(self.menu_tab)
        self.quantity_entry.grid(row=2, column=1, padx=10, pady=10)

        self.order_button = ttk.Button(self.menu_tab, text="Оформить заказ", command=self.place_order)
        self.order_button.grid(row=3, column=0, columnspan=2, pady=20)

    def load_products(self, event):
        category = self.category_combobox.get()
        conn = sqlite3.connect('cafe.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products WHERE category = ?", (category,))
        self.products = c.fetchall()
        conn.close()
        self.product_combobox['values'] = [f"{product[1]} ({product[3]} шт.)" for product in self.products]
        self.products_dict = {product[1]: product for product in self.products}

    def place_order(self):
        product_name = self.product_combobox.get().split(" (")[0]
        quantity = int(self.quantity_entry.get())
        product = self.products_dict.get(product_name)
        if product and product[3] >= quantity:
            messagebox.showinfo("Заказ", f"Заказ оформлен: {product_name}, {quantity} шт.")
        else:
            messagebox.showerror("Ошибка", "Недостаточно товара на складе.")

    def create_inventory_tab(self):
        tree = ttk.Treeview(self.inventory_tab, columns=("ID", "Название", "Цена", "Кол-во", "Категория"))
        tree.heading("#1", text="ID")
        tree.heading("#2", text="Название")
        tree.heading("#3", text="Цена")
        tree.heading("#4", text="Кол-во")
        tree.heading("#5", text="Категория")
        tree.pack(expand=True, fill="both")
        conn = sqlite3.connect('cafe.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def create_statistics_tab(self):
        self.stat_type_combobox = ttk.Combobox(self.statistics_tab, values=["Круговая диаграмма", "Таблица заказов"])
        self.stat_type_combobox.pack(pady=10)
        self.stat_type_combobox.bind("<<ComboboxSelected>>", self.switch_statistics)

        self.statistics_frame = ttk.Frame(self.statistics_tab)
        self.statistics_frame.pack(expand=True, fill="both")

        self.load_pie_chart()

    def switch_statistics(self, event):
        for widget in self.statistics_frame.winfo_children():
            widget.destroy()
        if self.stat_type_combobox.get() == "Круговая диаграмма":
            self.load_pie_chart()
        else:
            self.load_orders_table()

    def load_pie_chart(self):
        conn = sqlite3.connect('cafe.db')
        c = conn.cursor()
        c.execute("SELECT category, SUM(stock) FROM products GROUP BY category")
        data = c.fetchall()
        conn.close()
        if data:
            categories = [item[0] for item in data]
            quantities = [item[1] for item in data]
            fig = Figure(figsize=(6, 6))
            ax = fig.add_subplot(111)
            ax.pie(quantities, labels=categories, autopct='%1.1f%%', startangle=140)
            ax.set_title("Распределение товаров по категориям")
            canvas = FigureCanvasTkAgg(fig, master=self.statistics_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()

    def load_orders_table(self):
        tree = ttk.Treeview(self.statistics_frame, columns=("ID", "Название", "Цена", "Кол-во", "Категория"))
        tree.heading("#1", text="ID")
        tree.heading("#2", text="Название")
        tree.heading("#3", text="Цена")
        tree.heading("#4", text="Кол-во")
        tree.heading("#5", text="Категория")
        tree.pack(expand=True, fill="both")
        conn = sqlite3.connect('cafe.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

if __name__ == "__main__":
    create_and_fill_db()
    root = tk.Tk()
    app = CafeApp(root)
    root.mainloop()
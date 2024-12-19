import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3


class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет товаров на складе")

        self.conn = sqlite3.connect("warehouse.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both")

        self.input_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.input_tab, text="Добавить товар")
        self.create_input_tab()

        self.manage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_tab, text="Управление товарами")
        self.create_manage_tab()

        self.table_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.table_tab, text="Список товаров")
        self.create_table_tab()

        self.report_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.report_tab, text="Отчеты")
        self.create_report_tab()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            supplier TEXT NOT NULL,
            date TEXT NOT NULL
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            date TEXT NOT NULL
        )
        """)
        self.conn.commit()

    def create_input_tab(self):
        ttk.Label(self.input_tab, text="Поставщик:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        ttk.Label(self.input_tab, text="Название товара:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        ttk.Label(self.input_tab, text="Количество:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        ttk.Label(self.input_tab, text="Дата поступления\n(YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=5, sticky="e")

        self.supplier_entry = ttk.Entry(self.input_tab)
        self.supplier_entry.grid(row=0, column=1, padx=10, pady=5)

        self.product_name_entry = ttk.Entry(self.input_tab)
        self.product_name_entry.grid(row=1, column=1, padx=10, pady=5)

        self.quantity_entry = ttk.Entry(self.input_tab)
        self.quantity_entry.grid(row=2, column=1, padx=10, pady=5)

        self.date_entry = ttk.Entry(self.input_tab)
        self.date_entry.grid(row=3, column=1, padx=10, pady=5)

        self.add_button = ttk.Button(self.input_tab, text="Добавить товар", command=self.add_product)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

    def create_manage_tab(self):
        ttk.Label(self.manage_tab, text="Название товара:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        ttk.Label(self.manage_tab, text="Количество (убрать):").grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.manage_product_name_entry = ttk.Entry(self.manage_tab)
        self.manage_product_name_entry.grid(row=0, column=1, padx=10, pady=5)

        self.manage_quantity_entry = ttk.Entry(self.manage_tab)
        self.manage_quantity_entry.grid(row=1, column=1, padx=10, pady=5)

        self.remove_button = ttk.Button(self.manage_tab, text="Убрать товар", command=self.remove_product)
        self.remove_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_table_tab(self):
        columns = ("name", "quantity", "supplier", "date")

        self.tree = ttk.Treeview(self.table_tab, columns=columns, show="headings")
        self.tree.heading("name", text="Название товара")
        self.tree.heading("quantity", text="Количество")
        self.tree.heading("supplier", text="Поставщик")
        self.tree.heading("date", text="Дата поступления")
        
        self.tree.column("name", width=150)
        self.tree.column("quantity", width=100)
        self.tree.column("supplier", width=150)
        self.tree.column("date", width=100)

        self.tree.pack(expand=True, fill="both")

        self.update_table()

    def create_report_tab(self):
        ttk.Label(self.report_tab, text="Выберите период:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.period_combo = ttk.Combobox(self.report_tab, values=["Месяц", "Квартал", "Год"])
        self.period_combo.grid(row=0, column=1, padx=10, pady=5)

        self.generate_report_button = ttk.Button(self.report_tab, text="Сформировать отчет", command=self.generate_report)
        self.generate_report_button.grid(row=1, column=0, columnspan=2, pady=10)

        self.report_text = tk.Text(self.report_tab, height=20, width=80)
        self.report_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def add_product(self):
        supplier = self.supplier_entry.get()
        name = self.product_name_entry.get()
        quantity = self.quantity_entry.get()
        date = self.date_entry.get()

        if not (supplier and name and quantity and date):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть числом!")
            return

        self.cursor.execute("""
        INSERT INTO products (name, quantity, supplier, date)
        VALUES (?, ?, ?, ?)
        """, (name, quantity, supplier, date))
        self.cursor.execute("""
        INSERT INTO transactions (type, name, quantity, date)
        VALUES (?, ?, ?, ?)
        """, ("add", name, quantity, date))
        self.conn.commit()

        messagebox.showinfo("Успех", "Товар успешно добавлен!")
        self.clear_input_fields()
        self.update_table()

    def remove_product(self):
        name = self.manage_product_name_entry.get()
        quantity = self.manage_quantity_entry.get()

        if not (name and quantity):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("Ошибка", "Количество должно быть числом!")
            return

        self.cursor.execute("SELECT quantity FROM products WHERE name = ?", (name,))
        product = self.cursor.fetchone()

        if product and product[0] >= quantity:
            self.cursor.execute("""
            UPDATE products SET quantity = quantity - ? WHERE name = ?
            """, (quantity, name))
            self.cursor.execute("""
            INSERT INTO transactions (type, name, quantity, date)
            VALUES (?, ?, ?, ?)
            """, ("remove", name, quantity, datetime.now().strftime("%Y-%m-%d")))
            if product[0] == quantity:
                self.cursor.execute("DELETE FROM products WHERE name = ?", (name,))
            self.conn.commit()

            messagebox.showinfo("Успех", "Товар успешно удален!")
            self.update_table()
        else:
            messagebox.showerror("Ошибка", "Недостаточно товара или товар не найден!")

    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("SELECT name, quantity, supplier, date FROM products")
        for product in self.cursor.fetchall():
            self.tree.insert("", tk.END, values=product)

    def generate_report(self):
        period = self.period_combo.get()
        if not period:
            messagebox.showerror("Ошибка", "Выберите период для отчета!")
            return

        now = datetime.now()
        filtered_transactions = []

        query = "SELECT type, name, quantity, date FROM transactions WHERE strftime('%Y-%m', date) = ?"
        if period == "Месяц":
            date_filter = now.strftime("%Y-%m")
        elif period == "Квартал":
            quarter = (now.month - 1) // 3 + 1
            date_filter = f"{now.year}-{quarter * 3:02}"
        elif period == "Год":
            date_filter = now.strftime("%Y")

        self.cursor.execute(query, (date_filter,))
        filtered_transactions = self.cursor.fetchall()

        report = ""
        for transaction in filtered_transactions:
            report += f"{transaction[3]} - {transaction[0].capitalize()} - {transaction[1]} - {transaction[2]}\n"

        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)

    def clear_input_fields(self):
        self.supplier_entry.delete(0, tk.END)
        self.product_name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()

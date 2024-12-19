import tkinter as tk
from tkinter import ttk, messagebox
import plotly.express as px
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import sqlite3
import threading

def create_db():
    conn = sqlite3.connect('budget_db.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS budget (
                    id INTEGER PRIMARY KEY,
                    category TEXT,
                    amount INTEGER,
                    start_date TEXT,
                    end_date TEXT)''')
    conn.commit()
    conn.close()

def add_data_to_db(category, amount, start_date, end_date):
    conn = sqlite3.connect('budget_db.db')
    c = conn.cursor()
    c.execute("INSERT INTO budget (category, amount, start_date, end_date) VALUES (?, ?, ?, ?)",
              (category, amount, start_date, end_date))
    conn.commit()
    conn.close()

def get_data_from_db(start_date, end_date):
    conn = sqlite3.connect('budget_db.db')
    c = conn.cursor()
    c.execute("SELECT category, amount FROM budget WHERE start_date >= ? AND end_date <= ?",
              (start_date, end_date))
    rows = c.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=['Категория', 'Сумма (млн. руб.)'])

def get_all_reports_from_db():
    conn = sqlite3.connect('budget_db.db')
    c = conn.cursor()
    c.execute("SELECT id, category, amount, start_date, end_date FROM budget")
    rows = c.fetchall()
    conn.close()
    return rows

def show_plot(data):
    fig = px.pie(data, names='Категория', values='Сумма (млн. руб.)', title='Распределение бюджета')
    fig.show()

def create_pdf(data, start_date, end_date, filename="report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)

    pdfmetrics.registerFont(TTFont('typehelvetica_uzk_editedbyl', 'typehelvetica_uzk_editedbyl.otf'))

    c = canvas.Canvas(filename, pagesize=letter)

    c.setFont("typehelvetica_uzk_editedbyl", 12)

    c.drawString(100, 750, "Отчет по распределению государственного бюджета")
    c.drawString(100, 730, f"Период: с {start_date} по {end_date}")
    
    c.drawString(100, 700, "Категория")
    c.drawString(300, 700, "Сумма (млн. руб.)")
    
    y_position = 680
    total_sum = 0
    
    for _, row in data.iterrows():
        c.drawString(100, y_position, row['Категория'])
        c.drawString(300, y_position, str(row['Сумма (млн. руб.)']))
        
        y_position -= 20
        total_sum += row['Сумма (млн. руб.)']
        
    y_position -= 20
    c.drawString(100, y_position, "Итого:")
    c.drawString(300, y_position, str(total_sum))
    
    c.save()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Управление МинФин РФ")
        self.root.geometry("960x420")
        
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=6)
        style.configure("TLabel", font=("Arial", 12))
        style.configure("TEntry", font=("Arial", 12), padding=5)

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Ввод данных")

        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Генерация отчетов")

        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text="Просмотр отчетов")

        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="Список отчетов")

        self.create_tab1_widgets()
        self.create_tab2_widgets()
        self.create_tab3_widgets()
        self.create_tab4_widgets()

    def create_tab1_widgets(self):
        tk.Label(self.tab1, text="Категория:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.category_entry = ttk.Entry(self.tab1)
        self.category_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.tab1, text="Сумма (млн. руб.):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = ttk.Entry(self.tab1)
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.tab1, text="Начальная дата (dd.mm.yyyy):").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.start_date_entry = ttk.Entry(self.tab1)
        self.start_date_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.tab1, text="Конечная дата (dd.mm.yyyy):").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.end_date_entry = ttk.Entry(self.tab1)
        self.end_date_entry.grid(row=3, column=1, padx=10, pady=10)

        ttk.Button(self.tab1, text="Добавить данные", command=self.on_add_data).grid(row=4, column=0, columnspan=2, pady=20)

    def create_tab2_widgets(self):
        tk.Label(self.tab2, text="Начальная дата (dd.mm.yyyy):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.start_date_report_entry = ttk.Entry(self.tab2)
        self.start_date_report_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.tab2, text="Конечная дата (dd.mm.yyyy):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.end_date_report_entry = ttk.Entry(self.tab2)
        self.end_date_report_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(self.tab2, text="Генерировать отчет", command=self.on_generate_report).grid(row=2, column=0, columnspan=2, pady=20)

    def create_tab3_widgets(self):
        tk.Label(self.tab3, text="Введите даты для просмотра отчетов:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.start_date_view_entry = ttk.Entry(self.tab3)
        self.start_date_view_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.tab3, text="Конечная дата:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.end_date_view_entry = ttk.Entry(self.tab3)
        self.end_date_view_entry.grid(row=1, column=1, padx=10, pady=10)

        ttk.Button(self.tab3, text="Просмотреть отчет", command=self.on_view_report).grid(row=2, column=0, columnspan=2, pady=20)

    def create_tab4_widgets(self):
        self.report_treeview = ttk.Treeview(self.tab4, columns=("ID", "Категория", "Сумма", "Дата начала", "Дата конца"), show="headings")
        self.report_treeview.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.report_treeview.heading("ID", text="ID")
        self.report_treeview.heading("Категория", text="Категория")
        self.report_treeview.heading("Сумма", text="Сумма (млн. руб.)")
        self.report_treeview.heading("Дата начала", text="Дата начала")
        self.report_treeview.heading("Дата конца", text="Дата конца")

        self.load_reports()

        self.tab4.grid_columnconfigure(0, weight=1)

        self.report_treeview.column("ID", width=54, anchor="center")
        self.report_treeview.column("Категория", anchor="w", stretch=True)
        self.report_treeview.column("Сумма", anchor="w", stretch=True)
        self.report_treeview.column("Дата начала", anchor="w", stretch=True)
        self.report_treeview.column("Дата конца", anchor="w", stretch=True)

    def load_reports(self):
        reports = get_all_reports_from_db()
        for report in reports:
            self.report_treeview.insert("", "end", values=report)

    def on_add_data(self):
        category = self.category_entry.get()
        amount = self.amount_entry.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        if not category or not amount or not start_date or not end_date:
            messagebox.showerror("Ошибка", "Пожалуйста, заполните все поля!")
            return

        try:
            amount = int(amount)
            add_data_to_db(category, amount, start_date, end_date)
            self.load_reports()
            messagebox.showinfo("Успех", "Данные успешно добавлены!")
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректную сумму!")

    def on_generate_report(self):
        start_date = self.start_date_report_entry.get()
        end_date = self.end_date_report_entry.get()

        if not start_date or not end_date:
            messagebox.showerror("Ошибка", "Пожалуйста, введите обе даты!")
            return

        threading.Thread(target=self.generate_report_thread, args=(start_date, end_date)).start()
   
    def generate_report_thread(self, start_date, end_date):
        data = get_data_from_db(start_date, end_date)
        if data.empty:
            messagebox.showerror("Ошибка", "Нет данных за выбранный период!")
            return

        show_plot(data)
        create_pdf(data, start_date, end_date)
        messagebox.showinfo("Успех", "Отчет успешно сгенерирован!")

    def on_view_report(self):
        start_date = self.start_date_view_entry.get()
        end_date = self.end_date_view_entry.get()

        if not start_date or not end_date:
            messagebox.showerror("Ошибка", "Пожалуйста, введите обе даты!")
            return

        threading.Thread(target=self.view_report_thread, args=(start_date, end_date)).start()
   
    def view_report_thread(self, start_date, end_date):
        data = get_data_from_db(start_date, end_date)
        if data.empty:
            messagebox.showerror("Ошибка", "Нет данных за выбранный период!")
            return

        show_plot(data)
        
if __name__ == "__main__":
    create_db()
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

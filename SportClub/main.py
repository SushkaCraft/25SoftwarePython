import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta

def connect_db():
    return sqlite3.connect('sports_club.db')

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        duration INTEGER NOT NULL,
                        cost REAL NOT NULL,
                        start_time TEXT NOT NULL''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS purchases (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER,
                        subscription_id INTEGER,
                        discount BOOLEAN,
                        FOREIGN KEY(client_id) REFERENCES clients(id),
                        FOREIGN KEY(subscription_id) REFERENCES subscriptions(id))''')
    
    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1080x480")
        self.root.title("Управление спортивным клубом")

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), padding=5)
        style.configure('TButton', font=('Arial', 12), padding=5)
        style.configure('TEntry', font=('Arial', 12), padding=5)
        style.configure('Treeview', font=('Arial', 10), rowheight=12)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.purchase_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.purchase_tab, text="Приобрести Абонимент")

        self.add_subscription_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_subscription_tab, text="Добавить Абонимент")

        self.add_client_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.add_client_tab, text="Добавить клиента")

        self.active_subscriptions_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.active_subscriptions_tab, text="Действующие абонименты")

        create_tables()
        self.create_purchase_tab()
        self.create_add_subscription_tab()
        self.create_add_client_tab()
        self.create_active_subscriptions_tab()

    def create_purchase_tab(self):
        frame = ttk.Frame(self.purchase_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Абонимент:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.combobox_subscription = ttk.Combobox(frame, state="readonly")
        self.combobox_subscription.grid(row=0, column=1, padx=10, pady=5)
        self.combobox_subscription.bind("<<ComboboxSelected>>", self.update_subscription_details)

        ttk.Label(frame, text="Время:").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.label_limit_time = ttk.Label(frame, text="")
        self.label_limit_time.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Приобритается:").grid(row=2, column=0, sticky="W", padx=10, pady=5)
        self.label_start_time = ttk.Label(frame, text="")
        self.label_start_time.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Кончается:").grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.label_end_time = ttk.Label(frame, text="")
        self.label_end_time.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Скидка 20%:").grid(row=4, column=0, sticky="W", padx=10, pady=5)
        self.toggle_discount_var = tk.BooleanVar()
        self.toggle_discount = ttk.Checkbutton(frame, variable=self.toggle_discount_var)
        self.toggle_discount.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Клиент:").grid(row=5, column=0, sticky="W", padx=10, pady=5)
        self.combobox_client = ttk.Combobox(frame, state="readonly")
        self.combobox_client.grid(row=5, column=1, padx=10, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Приобрести абонимент", command=self.purchase_subscription).pack(side="left", padx=5)

        self.display_clients_for_purchase()
        self.display_subscriptions_for_purchase()

    def create_add_subscription_tab(self):
        frame = ttk.Frame(self.add_subscription_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Название абонимента:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.entry_subscription_name = ttk.Entry(frame)
        self.entry_subscription_name.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Длительность (в днях):").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.entry_duration = ttk.Entry(frame)
        self.entry_duration.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Стоимость:").grid(row=2, column=0, sticky="W", padx=10, pady=5)
        self.entry_cost = ttk.Entry(frame)
        self.entry_cost.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Часы работы (например 8:00-12:00):").grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.entry_hours = ttk.Entry(frame)
        self.entry_hours.grid(row=3, column=1, padx=10, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить абонимент", command=self.add_subscription).pack(side="left", padx=5)

    def create_add_client_tab(self):
        frame = ttk.Frame(self.add_client_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="ФИО клиента:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.entry_client_name = ttk.Entry(frame)
        self.entry_client_name.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Возраст клиента:").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.entry_client_age = ttk.Entry(frame)
        self.entry_client_age.grid(row=1, column=1, padx=10, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить клиента", command=self.add_client).pack(side="left", padx=5)

    def create_active_subscriptions_tab(self):
        frame = ttk.Frame(self.active_subscriptions_tab, padding=20)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame, columns=("ID", "Client", "Subscription", "Start Date", "End Date", "Days Left"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Client", text="Клиент")
        self.tree.heading("Subscription", text="Абонимент")
        self.tree.heading("Start Date", text="Дата начала")
        self.tree.heading("End Date", text="Дата окончания")
        self.tree.heading("Days Left", text="Дни до окончания")
        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.column("ID", width=72, anchor="center")
        self.tree.column("Client", width=72, anchor="w")
        self.tree.column("Subscription", width=72, anchor="w")
        self.tree.column("Start Date", width=72, anchor="center")
        self.tree.column("End Date", width=72, anchor="center")
        self.tree.column("Days Left", width=72, anchor="center")

        self.display_active_subscriptions()

    def add_subscription(self):
        name = self.entry_subscription_name.get()
        duration = self.entry_duration.get()
        cost = self.entry_cost.get()
        hours = self.entry_hours.get()

        if name and duration and cost and hours:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subscriptions (name, duration, cost, start_time) VALUES (?, ?, ?, ?)", 
                           (name, duration, cost, hours))
            conn.commit()
            conn.close()
            self.display_subscriptions_for_purchase()
            messagebox.showinfo("Успех", "Абонимент добавлен!")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля.")

    def add_client(self):
        name = self.entry_client_name.get()
        age = self.entry_client_age.get()

        if name and age:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (name, age) VALUES (?, ?)", (name, age))
            conn.commit()
            conn.close()
            self.display_clients_for_purchase()
            messagebox.showinfo("Успех", "Клиент добавлен!")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля.")

    def purchase_subscription(self):
        client_name = self.combobox_client.get()
        subscription_name = self.combobox_subscription.get()

        if client_name and subscription_name:
            conn = connect_db()
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM clients WHERE name = ?", (client_name,))
            client_id = cursor.fetchone()
            if client_id:
                client_id = client_id[0]
            else:
                messagebox.showerror("Ошибка", "Клиент не найден.")
                return

            cursor.execute("SELECT id, duration, start_time FROM subscriptions WHERE name = ?", (subscription_name,))
            subscription = cursor.fetchone()
            if subscription:
                subscription_id = subscription[0]
                duration = subscription[1]
            else:
                messagebox.showerror("Ошибка", "Абонимент не найден.")
                return

            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration)

            self.label_start_time.config(text=start_date.strftime("%Y-%m-%d"))
            self.label_end_time.config(text=end_date.strftime("%Y-%m-%d"))

            discount = self.toggle_discount_var.get()
            cursor.execute("INSERT INTO purchases (client_id, subscription_id, discount) VALUES (?, ?, ?)", 
                        (client_id, subscription_id, discount))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Абонимент куплен!")
        else:
            messagebox.showerror("Ошибка", "Выберите клиента и абонимент.")

    def display_subscriptions_for_purchase(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscriptions")
        subscriptions = cursor.fetchall()
        conn.close()

        self.combobox_subscription['values'] = [subscription[1] for subscription in subscriptions]

    def display_clients_for_purchase(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM clients")
        clients = cursor.fetchall()
        conn.close()

        self.combobox_client['values'] = [client[1] for client in clients]
        self.combobox_client.set('')
    
    def update_subscription_details(self, event):
        subscription_name = self.combobox_subscription.get()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT duration, start_time FROM subscriptions WHERE name = ?", (subscription_name,))
        subscription = cursor.fetchone()
        conn.close()
        
        if subscription:
            duration = subscription[0]
            start_time = datetime.now()
            end_time = start_time + timedelta(days=duration)
            self.label_start_time.config(text=start_time.strftime("%Y-%m-%d"))
            self.label_end_time.config(text=end_time.strftime("%Y-%m-%d"))

            start_time_hours = subscription[1]
            if start_time == "Безлимит":
                self.label_limit_time.config(text="Безлимит")
            else:
                self.label_limit_time.config(text=f"{start_time_hours}")

    def display_active_subscriptions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT p.id, c.name, s.name, s.start_day, s.duration FROM purchases p "
                    "JOIN clients c ON p.client_id = c.id "
                    "JOIN subscriptions s ON p.subscription_id = s.id")
        purchases = cursor.fetchall()
        conn.close()

        for purchase in purchases:
            start_date_str = purchase[3]
            duration = purchase[4]
            
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

            end_date = start_date + timedelta(days=duration)
            days_left = (end_date - datetime.now()).days

            self.tree.insert("", "end", values=(
                purchase[0],
                purchase[1],
                purchase[2],
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                days_left
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

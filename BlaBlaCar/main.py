import tkinter as tk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
import requests
import sqlite3




def get_coordinates(address):
    API_KEY = "e3c8cb74f3b2420b937e89abc7cb6175"
    url = f"https://api.opencagedata.com/geocode/v1/json?q={address}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            lat = data['results'][0]['geometry']['lat']
            lng = data['results'][0]['geometry']['lng']
            return lat, lng
    return None, None

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск попутчиков")
        self.root.geometry("920x720")
        self.root.minsize(860, 640)

        self.conn = sqlite3.connect("rides.db")
        self.cursor = sqlite3.Cursor(self.conn)
        self.create_tables()

        self.setup_ui()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start TEXT NOT NULL,
                destination TEXT NOT NULL,
                date TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                message TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.create_route_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.create_route_tab, text="Создать маршрут")
        self.setup_create_route_tab()

        self.search_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.search_tab, text="Поиск маршрутов")
        self.setup_search_tab()

        self.map_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.map_tab, text="Просмотреть маршрут")
        self.setup_map_tab()

        self.chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_tab, text="Чат")
        self.setup_chat_tab()

    def setup_create_route_tab(self):
        ttk.Label(self.create_route_tab, text="Откуда:", font=("Arial", 14)).grid(row=0, column=0, padx=20, pady=20)
        self.start_entry = ttk.Entry(self.create_route_tab, font=("Arial", 14))
        self.start_entry.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        ttk.Label(self.create_route_tab, text="Куда:", font=("Arial", 14)).grid(row=1, column=0, padx=20, pady=20)
        self.destination_entry = ttk.Entry(self.create_route_tab, font=("Arial", 14))
        self.destination_entry.grid(row=1, column=1, padx=20, pady=20, sticky="ew")

        ttk.Label(self.create_route_tab, text="Дата:", font=("Arial", 14)).grid(row=2, column=0, padx=20, pady=20)
        self.date_entry = ttk.Entry(self.create_route_tab, font=("Arial", 14))
        self.date_entry.grid(row=2, column=1, padx=20, pady=20, sticky="ew")

        ttk.Label(self.create_route_tab, text="Цена:", font=("Arial", 14)).grid(row=3, column=0, padx=20, pady=20)
        self.price_entry = ttk.Entry(self.create_route_tab, font=("Arial", 14))
        self.price_entry.grid(row=3, column=1, padx=20, pady=20, sticky="ew")

        self.add_route_button = ttk.Button(self.create_route_tab, text="Добавить маршрут", command=self.add_route, style="TButton")
        self.add_route_button.grid(row=4, column=0, columnspan=2, pady=30)

    def add_route(self):
        start = self.start_entry.get()
        destination = self.destination_entry.get()
        date = self.date_entry.get()
        price = self.price_entry.get()

        if not start or not destination or not date or not price:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return

        try:
            price = float(price)
            self.cursor.execute("INSERT INTO routes (start, destination, date, price) VALUES (?, ?, ?, ?)",
                                (start, destination, date, price))
            self.conn.commit()
            messagebox.showinfo("Успех", "Маршрут добавлен")
            self.clear_route_fields()
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")

    def clear_route_fields(self):
        self.start_entry.delete(0, tk.END)
        self.destination_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def setup_search_tab(self):
        ttk.Label(self.search_tab, text="Откуда:", font=("Arial", 14)).grid(row=0, column=0, padx=20, pady=20)
        self.search_start_entry = ttk.Entry(self.search_tab, font=("Arial", 14))
        self.search_start_entry.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

        ttk.Label(self.search_tab, text="Куда:", font=("Arial", 14)).grid(row=1, column=0, padx=20, pady=20)
        self.search_destination_entry = ttk.Entry(self.search_tab, font=("Arial", 14))
        self.search_destination_entry.grid(row=1, column=1, padx=20, pady=20, sticky="ew")

        self.search_button = ttk.Button(self.search_tab, text="Найти", command=self.search_routes)
        self.search_button.grid(row=2, column=0, columnspan=2, pady=20)

        self.routes_list = tk.Listbox(self.search_tab, height=15, font=("Arial", 12))
        self.routes_list.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        self.search_tab.rowconfigure(3, weight=1)
        self.search_tab.columnconfigure(1, weight=1)
    
    def setup_map_tab(self):
        ttk.Label(self.map_tab, text="Введите ID маршрута:", font=("Arial", 14)).pack(pady=10)
        self.route_id_entry = ttk.Entry(self.map_tab, font=("Arial", 14))
        self.route_id_entry.pack(pady=10)

        self.show_route_button = ttk.Button(self.map_tab, text="Показать маршрут", command=self.show_route_on_map)
        self.show_route_button.pack(pady=10)

        self.map_widget = TkinterMapView(self.map_tab, width=800, height=600)
        self.map_widget.pack(fill="both", expand=True)

    def add_route(self):
        start = self.start_entry.get()
        destination = self.destination_entry.get()
        date = self.date_entry.get()
        price = self.price_entry.get()

        if not start or not destination or not date or not price:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return

        try:
            price = float(price)
            self.cursor.execute("INSERT INTO routes (start, destination, date, price) VALUES (?, ?, ?, ?)",
                                (start, destination, date, price))
            self.conn.commit()
            messagebox.showinfo("Успех", "Маршрут добавлен")
            self.clear_route_fields()
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом")

    def show_route_on_map(self):
        route_id = self.route_id_entry.get()
        if not route_id.isdigit():
            messagebox.showerror("Ошибка", "ID маршрута должен быть числом")
            return

        self.cursor.execute("SELECT start, destination FROM routes WHERE id = ?", (route_id,))
        route = self.cursor.fetchone()

        if route:
            start, destination = route

            start_lat, start_lng = get_coordinates(start)
            if start_lat is None or start_lng is None:
                messagebox.showerror("Ошибка", f"Не удалось получить координаты для: {start}")
                return

            dest_lat, dest_lng = get_coordinates(destination)
            if dest_lat is None or dest_lng is None:
                messagebox.showerror("Ошибка", f"Не удалось получить координаты для: {destination}")
                return

            self.map_widget.set_position((start_lat + dest_lat) / 2, (start_lng + dest_lng) / 2)
            self.map_widget.set_marker(start_lat, start_lng, text=start)
            self.map_widget.set_marker(dest_lat, dest_lng, text=destination)
        else:
            messagebox.showerror("Ошибка", "Маршрут не найден")
    
    def clear_route_fields(self):
        self.start_entry.delete(0, tk.END)
        self.destination_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

    def search_routes(self):
        start_query = self.search_start_entry.get()
        destination_query = self.search_destination_entry.get()
        self.routes_list.delete(0, tk.END)

        self.cursor.execute(
            "SELECT * FROM routes WHERE start LIKE ? AND destination LIKE ?",
            (f"%{start_query}%", f"%{destination_query}%")
        )
        results = self.cursor.fetchall()

        if results:
            for route in results:
                self.routes_list.insert(
                    tk.END, f"ID {route[0]}: {route[1]} -> {route[2]} | {route[3]} | {route[4]} руб."
                )
        else:
            self.routes_list.insert(tk.END, "Маршруты не найдены")

    def setup_chat_tab(self):
        self.chat_tab.rowconfigure(0, weight=1)
        self.chat_tab.columnconfigure(0, weight=1)

        self.chat_display = tk.Text(self.chat_tab, state="disabled", height=20, font=("Arial", 12))
        self.chat_display.grid(row=0, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")

        ttk.Label(self.chat_tab, text="Имя:", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=10)
        self.name_entry = ttk.Entry(self.chat_tab, font=("Arial", 14))
        self.name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.chat_entry = ttk.Entry(self.chat_tab, font=("Arial", 14))
        self.chat_entry.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        self.send_button = ttk.Button(self.chat_tab, text="Отправить", command=self.send_message)
        self.send_button.grid(row=1, column=3, padx=10, pady=10)

        self.chat_tab.columnconfigure(1, weight=1)
        self.chat_tab.columnconfigure(2, weight=1)

        self.load_chat()
        self.schedule_chat_update()

    def schedule_chat_update(self):
        self.load_chat()
        self.root.after(500, self.schedule_chat_update)

    def send_message(self):
        name = self.name_entry.get()
        message = self.chat_entry.get()
        if name and message:
            self.cursor.execute("INSERT INTO chat (name, message) VALUES (?, ?)", (name, message))
            self.conn.commit()
            self.chat_entry.delete(0, tk.END)
            self.load_chat()
        else:
            messagebox.showerror("Ошибка", "Имя и сообщение не могут быть пустыми")

    def load_chat(self):
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)

        self.cursor.execute("SELECT name, message FROM chat")
        messages = self.cursor.fetchall()

        for name, message in messages:
            self.chat_display.insert(tk.END, f"{name}: {message}\n")

        self.chat_display.config(state="disabled")

    def close_app(self):
        self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.close_app)
    root.mainloop()
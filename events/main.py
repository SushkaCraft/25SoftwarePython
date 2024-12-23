import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

class Database:
    def __init__(self, db_name="events.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            date_time TEXT NOT NULL,
            total_seats INTEGER NOT NULL,
            remaining_seats INTEGER NOT NULL
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            guest_name TEXT NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )''')
        self.connection.commit()

    def add_event(self, name, location, date_time, total_seats):
        self.cursor.execute('''INSERT INTO events (name, location, date_time, total_seats, remaining_seats)
                               VALUES (?, ?, ?, ?, ?)''',
                            (name, location, date_time, total_seats, total_seats))
        self.connection.commit()

    def get_events(self):
        self.cursor.execute('SELECT * FROM events')
        return self.cursor.fetchall()

    def update_event_seats(self, event_id, remaining_seats):
        self.cursor.execute('UPDATE events SET remaining_seats = ? WHERE id = ?', (remaining_seats, event_id))
        self.connection.commit()

    def close(self):
        self.connection.close()

class EventApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Создание мероприятиями")
        self.root.geometry("960x480")

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), padding=5)
        style.configure('TButton', font=('Arial', 12), padding=5)
        style.configure('TEntry', font=('Arial', 12), padding=5)
        style.configure('Treeview', font=('Arial', 11), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

        self.db = Database()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_event_tab = ttk.Frame(self.notebook)
        self.register_tab = ttk.Frame(self.notebook)
        self.events_table_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.create_event_tab, text="Создать мероприятие")
        self.notebook.add(self.register_tab, text="Регистрация")
        self.notebook.add(self.events_table_tab, text="Список мероприятий")

        self.setup_create_event_tab()
        self.setup_register_tab()
        self.setup_events_table_tab()
        self.update_events_table()

    def setup_create_event_tab(self):
        frame = ttk.Frame(self.create_event_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Название мероприятия:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.event_name_entry = ttk.Entry(frame)
        self.event_name_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text="Место проведения:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.event_location_entry = ttk.Entry(frame)
        self.event_location_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text="Дата и время (ДД.ММ.ГГГГ ЧЧ:ММ):").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.event_date_time_entry = ttk.Entry(frame)
        self.event_date_time_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text="Количество мест:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.event_seats_entry = ttk.Entry(frame)
        self.event_seats_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(frame, text="Создать", command=self.create_event).grid(row=4, column=0, columnspan=2, pady=10)

    def setup_register_tab(self):
        frame = ttk.Frame(self.register_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Выберите мероприятие:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.event_combobox = ttk.Combobox(frame, state="readonly")
        self.event_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        ttk.Label(frame, text="ФИО:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.guest_name_entry = ttk.Entry(frame)
        self.guest_name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ttk.Button(frame, text="Зарегистрироваться", command=self.register_guest).grid(row=2, column=0, columnspan=2, pady=10)
        self.update_event_combobox()

    def setup_events_table_tab(self):
        frame = ttk.Frame(self.events_table_tab, padding=20)
        frame.pack(fill="both", expand=True)

        columns = ("ID", "Название", "Место", "Дата и время", "Всего мест", "Осталось мест")
        self.events_table = ttk.Treeview(frame, columns=columns, show="headings")

        for col in columns:
            self.events_table.heading(col, text=col)
            self.events_table.column(col, minwidth=0, width=144, anchor="w")

        self.events_table.pack(fill="both", expand=True)

        self.events_table.column("ID", width=54, anchor="center")

    def create_event(self):
        name = self.event_name_entry.get().strip()
        location = self.event_location_entry.get().strip()
        date_time_str = self.event_date_time_entry.get().strip()
        seats = self.event_seats_entry.get().strip()

        if not name or not location or not date_time_str or not seats:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        try:
            date_time = datetime.strptime(date_time_str, "%d.%m.%Y %H:%M")
            seats = int(seats)
            if seats <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные данные в поле даты/времени или количества мест.")
            return

        self.db.add_event(name, location, date_time_str, seats)
        self.update_event_combobox()
        self.update_events_table()
        messagebox.showinfo("Успех", "Мероприятие успешно создано!")

    def update_event_combobox(self):
        events = self.db.get_events()
        self.event_combobox["values"] = [f"{event[1]} ({event[3]})" for event in events]

    def update_events_table(self):
        for row in self.events_table.get_children():
            self.events_table.delete(row)

        events = self.db.get_events()
        for event in events:
            self.events_table.insert("", "end", values=(
                event[0], event[1], event[2], event[3], event[4], event[5]
            ))

    def register_guest(self):
        selected_event_index = self.event_combobox.current()
        guest_name = self.guest_name_entry.get().strip()

        if selected_event_index == -1 or not guest_name:
            messagebox.showerror("Ошибка", "Выберите мероприятие и укажите ФИО!")
            return

        events = self.db.get_events()
        event = events[selected_event_index]

        if event[5] <= 0:
            messagebox.showerror("Ошибка", "На мероприятии больше нет свободных мест!")
            return

        self.db.update_event_seats(event[0], event[5] - 1)
        self.update_events_table()
        messagebox.showinfo("Успех", f"{guest_name} успешно зарегистрирован на мероприятие {event[1]}!")

if __name__ == "__main__":
    root = tk.Tk()
    app = EventApp(root)
    root.mainloop()

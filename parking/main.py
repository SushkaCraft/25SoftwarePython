import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta

def connect_db():
    return sqlite3.connect('parking.db')

def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS parkings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS parking_spots (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parking_id INTEGER,
                        spot_number INTEGER,
                        is_booked BOOLEAN,
                        booked_by TEXT,
                        book_date TEXT,
                        end_date TEXT,
                        FOREIGN KEY (parking_id) REFERENCES parkings(id)
                    )''')
    
    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1120x480")
        self.root.title("Управление парковками")

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), padding=5)
        style.configure('TButton', font=('Arial', 12), padding=5)
        style.configure('TEntry', font=('Arial', 12), padding=5)
        style.configure('Treeview', font=('Arial', 11), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_parking_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.create_parking_tab, text="Создание парковки")

        self.booking_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.booking_tab, text="Бронирование места")

        self.booked_spots_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.booked_spots_tab, text="Занятые места")

        self.create_create_parking_tab()
        self.create_booking_tab()
        self.create_booked_spots_tab()

    def create_create_parking_tab(self):
        frame = ttk.Frame(self.create_parking_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Название парковки:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.entry_parking_name = ttk.Entry(frame)
        self.entry_parking_name.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Количество мест:").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.entry_spot_count = ttk.Entry(frame)
        self.entry_spot_count.grid(row=1, column=1, padx=10, pady=5)

        ttk.Button(frame, text="Создать парковку", command=self.create_parking).grid(row=2, column=0, columnspan=2, pady=10)

    def create_booking_tab(self):
        frame = ttk.Frame(self.booking_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Выберите парковку:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.combobox_parking = ttk.Combobox(frame, state="readonly")
        self.combobox_parking.grid(row=0, column=1, padx=10, pady=5)
        self.combobox_parking.bind("<<ComboboxSelected>>", self.load_available_spots)

        ttk.Label(frame, text="Выберите место:").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.combobox_spot = ttk.Combobox(frame, state="readonly")
        self.combobox_spot.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Имя бронирующего:").grid(row=2, column=0, sticky="W", padx=10, pady=5)
        self.entry_booking_name = ttk.Entry(frame)
        self.entry_booking_name.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Количество часов:").grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.entry_booking_hours = ttk.Entry(frame)
        self.entry_booking_hours.grid(row=3, column=1, padx=10, pady=5)

        ttk.Button(frame, text="Забронировать место", command=self.book_parking_spot).grid(row=4, column=0, columnspan=2, pady=10)

    def create_booked_spots_tab(self):
        frame = ttk.Frame(self.booked_spots_tab, padding=20)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            frame,
            columns=("ID", "Parking Name", "Spot Number", "Booked By", "Book Date", "End Date"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Parking Name", text="Название парковки")
        self.tree.heading("Spot Number", text="Номер места")
        self.tree.heading("Booked By", text="Кто забронировал")
        self.tree.heading("Book Date", text="Дата брони")
        self.tree.heading("End Date", text="Дата окончания")

        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.column("ID", width=54, anchor="center")

        self.display_booked_spots()

    def create_parking(self):
        parking_name = self.entry_parking_name.get()
        spot_count = self.entry_spot_count.get()

        if parking_name and spot_count.isdigit():
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO parkings (name) VALUES (?)", (parking_name,))
            parking_id = cursor.lastrowid
            conn.commit()

            for spot_number in range(1, int(spot_count) + 1):
                cursor.execute("INSERT INTO parking_spots (parking_id, spot_number, is_booked, booked_by, book_date, end_date) VALUES (?, ?, ?, ?, ?, ?)", 
                               (parking_id, spot_number, False, None, None, None))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", f"Парковка '{parking_name}' создана с {spot_count} местами!")
            self.load_parkings()
        else:
            messagebox.showerror("Ошибка", "Введите корректные данные для парковки!")

    def load_parkings(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM parkings")
        parkings = cursor.fetchall()
        conn.close()

        self.combobox_parking['values'] = [name for _, name in parkings]
        self.combobox_parking.set('')

    def load_available_spots(self, event=None):
        parking_name = self.combobox_parking.get()
        if not parking_name:
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM parkings WHERE name = ?", (parking_name,))
        parking_id = cursor.fetchone()[0]

        cursor.execute("SELECT spot_number FROM parking_spots WHERE parking_id = ? AND is_booked = 0", (parking_id,))
        available_spots = cursor.fetchall()
        conn.close()

        self.combobox_spot['values'] = [str(spot[0]) for spot in available_spots]
        self.combobox_spot.set('')

    def book_parking_spot(self):
        parking_name = self.combobox_parking.get()
        spot_number = self.combobox_spot.get()
        booking_name = self.entry_booking_name.get()
        booking_hours = self.entry_booking_hours.get()

        if parking_name and spot_number and booking_name and booking_hours.isdigit():
            booking_hours = int(booking_hours)
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM parkings WHERE name = ?", (parking_name,))
            parking_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM parking_spots WHERE parking_id = ? AND spot_number = ? AND is_booked = 0", 
                           (parking_id, spot_number))
            spot = cursor.fetchone()

            if spot:
                start_time = datetime.now()
                end_time = start_time + timedelta(hours=booking_hours)
                
                cursor.execute("UPDATE parking_spots SET is_booked = 1, booked_by = ?, book_date = ?, end_date = ? WHERE id = ?",
                               (booking_name, start_time.strftime("%Y-%m-%d %H:%M:%S"), end_time.strftime("%Y-%m-%d %H:%M:%S"), spot[0]))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", f"Место {spot_number} успешно забронировано на {booking_hours} часов!")
                self.display_booked_spots()
            else:
                messagebox.showerror("Ошибка", "Это место уже занято или не существует!")
        else:
            messagebox.showerror("Ошибка", "Заполните все поля корректно!")

    def display_booked_spots(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''SELECT parking_spots.id, parkings.name, parking_spots.spot_number, parking_spots.booked_by, parking_spots.book_date, parking_spots.end_date
                          FROM parking_spots
                          JOIN parkings ON parking_spots.parking_id = parkings.id
                          WHERE parking_spots.is_booked = 1''')
        booked_spots = cursor.fetchall()
        conn.close()

        for spot in booked_spots:
            self.tree.insert("", "end", values=spot)

if __name__ == "__main__":
    create_table()
    root = tk.Tk()
    app = AppGUI(root)
    app.load_parkings()
    root.mainloop()

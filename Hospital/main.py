import sqlite3
import tkinter as tk
from tkinter import ttk
from tkhtmlview import HTMLLabel
import tkintermapview

def init_db():
    with sqlite3.connect("hospital.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS cabinets (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            floor INTEGER,
                            building TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS doctors (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            full_name TEXT NOT NULL,
                            position TEXT,
                            specialty TEXT,
                            cabinet TEXT,
                            work_time TEXT,
                            work_days TEXT)''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS ambulance_teams (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            team_name TEXT NOT NULL,
                            driver TEXT NOT NULL,
                            driver_name TEXT NOT NULL,
                            paramedic TEXT NOT NULL,
                            paramedic_name TEXT NOT NULL,
                            sanitary TEXT NOT NULL,
                            sanitary_name TEXT NOT NULL)''')

        cursor.execute("DELETE FROM cabinets")
        cursor.execute("DELETE FROM doctors")
        cursor.execute("DELETE FROM ambulance_teams")

        cabinets_data = [
            ("Регистратура", 1, ""),
            ("Кабинет терапевта", 2, ""),
            ("Хирургический кабинет", 3, ""),
            ("Стоматология", 1, ""),
            ("Кабинет офтальмолога", 2, ""),
            ("Кабинет кардиолога", 3, ""),
            ("Кабинет эндокринолога", 4, ""),
            ("Кабинет дерматолога", 1, ""),
        ]
        cursor.executemany("INSERT INTO cabinets (name, floor, building) VALUES (?, ?, ?)", cabinets_data)

        doctors_data = [
            ("Иванов Иван Иванович", "Терапевт", "Терапия", "Кабинет терапевта", "8:00-16:00", "Пн-Пт"),
            ("Петров Петр Петрович", "Хирург", "Хирургия", "Хирургический кабинет", "10:00-18:00", "Вт-Сб"),
            ("Сидоров Сидор Сидорович", "Стоматолог", "Стоматология", "Стоматология", "9:00-15:00", "Пн-Пт"),
            ("Алексеева Алена Алексеевна", "Кардиолог", "Кардиология", "Кабинет кардиолога", "9:00-17:00", "Пн-Пт"),
            ("Борисов Борис Борисович", "Эндокринолог", "Эндокринология", "Кабинет эндокринолога", "8:00-16:00", "Пн-Ср"),
            ("Михайлова Мария Михайловна", "Дерматолог", "Дерматология", "Кабинет дерматолога", "10:00-18:00", "Вт-Пт"),
        ]
        cursor.executemany("INSERT INTO doctors (full_name, position, specialty, cabinet, work_time, work_days) VALUES (?, ?, ?, ?, ?, ?)", doctors_data)

        ambulance_teams_data = [
            ("Бригада I", "Водитель - Иванов Иван Иванович", "", "Фельдшер - Петрова Ольга Сергеевна", "", "Санитар - Кузнецова Мария Васильевна", ""),
            ("Бригада II", "Водитель - Смирнов Алексей Михайлович", "", "Фельдшер - Иванова Наталья Владимировна", "", "Санитар - Васильев Сергей Александрович", ""),
        ]

        cursor.executemany("INSERT INTO ambulance_teams (team_name, driver, driver_name, paramedic, paramedic_name, sanitary, sanitary_name) VALUES (?, ?, ?, ?, ?, ?, ?)", ambulance_teams_data)

        conn.commit()

class HospitalApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Мед Учреждение")
        self.geometry("960x560")
        self.init_tabs()

    def init_tabs(self):
        tab_control = ttk.Notebook(self)

        self.cabinets_tab = ttk.Frame(tab_control)
        tab_control.add(self.cabinets_tab, text="Кабинеты")
        self.init_cabinets_tab()

        self.doctors_tab = ttk.Frame(tab_control)
        tab_control.add(self.doctors_tab, text="Дежурные Врачи")
        self.init_doctors_tab()

        self.map_tab = ttk.Frame(tab_control)
        tab_control.add(self.map_tab, text="Карта")
        self.init_map_tab()

        tab_control.pack(expand=1, fill="both")

    def init_cabinets_tab(self):
        ttk.Label(self.cabinets_tab, text="Список кабинетов", font=("Arial", 16)).grid(row=0, column=0, pady=10, columnspan=3)

        self.cabinet_list = tk.Listbox(self.cabinets_tab, height=20, width=144)
        self.cabinet_list.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.cabinets_tab.grid_columnconfigure(0, weight=1)

        self.load_cabinets()

    def load_cabinets(self):
        self.cabinet_list.delete(0, tk.END)
        with sqlite3.connect("hospital.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, floor, building FROM cabinets")
            for row in cursor.fetchall():
                self.cabinet_list.insert(tk.END, f"{row[0]} - Этаж {row[1]}")

    def init_doctors_tab(self):
        ttk.Label(self.doctors_tab, text="Список дежурных врачей", font=("Arial", 14)).grid(row=0, column=0, pady=10, columnspan=3)

        self.doctors_list = tk.Listbox(self.doctors_tab, height=16, width=144)
        self.doctors_list.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.doctors_tab.grid_columnconfigure(0, weight=1)

        self.load_doctors()

        ttk.Label(self.doctors_tab, text="Список бригад скорой помощи", font=("Arial", 14)).grid(row=3, column=0, pady=10, columnspan=3)

        self.ambulance_teams_list = tk.Listbox(self.doctors_tab, height=8, width=144)
        self.ambulance_teams_list.grid(row=4, column=0, padx=10, pady=10, sticky="ew")

        self.doctors_tab.grid_columnconfigure(0, weight=1)

        self.load_ambulance_teams()

    def load_doctors(self):
        self.doctors_list.delete(0, tk.END)
        with sqlite3.connect("hospital.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, position, cabinet, work_time, work_days FROM doctors")
            for row in cursor.fetchall():
                self.doctors_list.insert(tk.END, f"{row[0]} - {row[1]} - {row[2]} - {row[3]} ({row[4]})")

    def load_ambulance_teams(self):
        self.ambulance_teams_list.delete(0, tk.END)
        with sqlite3.connect("hospital.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT team_name, driver, paramedic, sanitary FROM ambulance_teams")
            for row in cursor.fetchall():
                self.ambulance_teams_list.insert(tk.END, f"{row[0]} - {row[1]}, {row[2]}, {row[3]}")

    def init_map_tab(self):
        ttk.Label(self.map_tab, text="Местоположение больницы", font=("Arial", 14)).pack(pady=10)

        map_widget = tkintermapview.TkinterMapView(self.map_tab, width=800, height=600, corner_radius=0)
        map_widget.pack(fill="both", expand=True)

        map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=48)

        map_widget.set_position(52.739902, 41.445765, marker=True)

if __name__ == "__main__":
    init_db()
    app = HospitalApp()
    app.mainloop()

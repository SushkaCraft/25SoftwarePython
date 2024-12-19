import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkintermapview import TkinterMapView

def create_db():
    try:
        conn = sqlite3.connect('transport_monitoring.db')
        c = conn.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS transport (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL,
            type TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        )''')
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось создать таблицу: {e}")
    finally:
        conn.close()

def add_transport_to_db(number, transport_type, latitude, longitude):
    try:
        conn = sqlite3.connect('transport_monitoring.db')
        c = conn.cursor()
        c.execute('''
        INSERT INTO transport (number, type, latitude, longitude)
        VALUES (?, ?, ?, ?)''', (number, transport_type, latitude, longitude))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось добавить транспорт: {e}")
    finally:
        conn.close()

def get_all_transport():
    try:
        conn = sqlite3.connect('transport_monitoring.db')
        c = conn.cursor()
        c.execute('SELECT * FROM transport')
        rows = c.fetchall()
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось получить данные: {e}")
        rows = []
    finally:
        conn.close()
    return rows

def get_transport_by_id(transport_id):
    try:
        conn = sqlite3.connect('transport_monitoring.db')
        c = conn.cursor()
        c.execute('SELECT * FROM transport WHERE id = ?', (transport_id,))
        row = c.fetchone()
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Не удалось получить транспорт: {e}")
        row = None
    finally:
        conn.close()
    return row

root = tk.Tk()
root.title('Система мониторинга транспорта')

tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Добавить транспорт')
tab_control.add(tab2, text='Просмотр транспорта')
tab_control.add(tab3, text='Карта')
tab_control.pack(expand=1, fill='both')

def add_transport():
    try:
        number = entry_number.get().strip()
        transport_type = entry_type.get().strip()
        latitude = float(entry_latitude.get().strip())
        longitude = float(entry_longitude.get().strip())

        if not number or not transport_type:
            raise ValueError("Все поля должны быть заполнены.")

        add_transport_to_db(number, transport_type, latitude, longitude)
        messagebox.showinfo("Успех", "Транспорт успешно добавлен.")
        clear_inputs()
    except ValueError as ve:
        messagebox.showwarning("Ошибка ввода", f"Некорректные данные: {ve}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

def clear_inputs():
    entry_number.delete(0, tk.END)
    entry_type.delete(0, tk.END)
    entry_latitude.delete(0, tk.END)
    entry_longitude.delete(0, tk.END)

tk.Label(tab1, text="Номер транспорта:").grid(row=0, column=0, padx=10, pady=10)
entry_number = tk.Entry(tab1)
entry_number.grid(row=0, column=1, padx=10, pady=10)

tk.Label(tab1, text="Тип транспорта:").grid(row=1, column=0, padx=10, pady=10)
entry_type = tk.Entry(tab1)
entry_type.grid(row=1, column=1, padx=10, pady=10)

tk.Label(tab1, text="Широта:").grid(row=2, column=0, padx=10, pady=10)
entry_latitude = tk.Entry(tab1)
entry_latitude.grid(row=2, column=1, padx=10, pady=10)

tk.Label(tab1, text="Долгота:").grid(row=3, column=0, padx=10, pady=10)
entry_longitude = tk.Entry(tab1)
entry_longitude.grid(row=3, column=1, padx=10, pady=10)

tk.Button(tab1, text="Добавить транспорт", command=add_transport).grid(row=4, column=0, columnspan=2, pady=20)

def show_transport():
    transport_list.delete(1.0, tk.END)
    rows = get_all_transport()
    for row in rows:
        transport_list.insert(tk.END, f"ID: {row[0]} | Номер: {row[1]} | Тип: {row[2]} | "
                                      f"Широта: {row[3]} | Долгота: {row[4]}\n")

tk.Button(tab2, text="Показать данные о транспорте", command=show_transport).pack(pady=10)
transport_list = tk.Text(tab2, width=50, height=15)
transport_list.pack(pady=10)

map_widget = TkinterMapView(tab3, width=800, height=600)
map_widget.pack(padx=10, pady=10)

def show_map():
    map_widget.set_position(55.7558, 37.6173)
    map_widget.set_zoom(10)
    rows = get_all_transport()
    for row in rows:
        map_widget.set_marker(row[3], row[4], text=f"{row[1]} - {row[2]}")

tk.Button(tab3, text="Обновить карту", command=show_map).pack(pady=10)

create_db()
root.mainloop()

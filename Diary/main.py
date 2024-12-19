import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import time
import threading

def create_db():
    conn = sqlite3.connect("calendar.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

def connect_db():
    return sqlite3.connect("calendar.db")

def add_event():
    def save_event():
        title = title_entry.get()
        description = desc_entry.get("1.0", tk.END).strip()
        date = date_entry.get()
        time = time_entry.get()

        if not title or not date:
            messagebox.showerror("Ошибка", "Название и дата обязательны!")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (title, description, date, time) VALUES (?, ?, ?, ?)",
                       (title, description, date, time))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Событие добавлено!")
        add_window.destroy()
        load_events()

    add_window = tk.Toplevel(root)
    add_window.title("Добавить событие")

    tk.Label(add_window, text="Название:").grid(row=0, column=0, padx=10, pady=5)
    title_entry = tk.Entry(add_window, width=30)
    title_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Описание:").grid(row=1, column=0, padx=10, pady=5)
    desc_entry = tk.Text(add_window, width=30, height=5)
    desc_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=5)
    date_entry = tk.Entry(add_window, width=30)
    date_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(add_window, text="Время (HH:MM):").grid(row=3, column=0, padx=10, pady=5)
    time_entry = tk.Entry(add_window, width=30)
    time_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Button(add_window, text="Сохранить", command=save_event).grid(row=4, column=0, columnspan=2, pady=10)

def load_events():
    for row in tree.get_children():
        tree.delete(row)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, date, time FROM events ORDER BY date, time")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)
    conn.close()

def delete_event():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите событие для удаления!")
        return

    event_id = tree.item(selected_item[0])["values"][0]
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()
    load_events()
    messagebox.showinfo("Успех", "Событие удалено!")

def edit_event():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Ошибка", "Выберите событие для редактирования!")
        return

    event_id = tree.item(selected_item[0])["values"][0]
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT title, description, date, time FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    conn.close()

    def save_changes():
        new_title = title_entry.get()
        new_description = desc_entry.get("1.0", tk.END).strip()
        new_date = date_entry.get()
        new_time = time_entry.get()

        if not new_title or not new_date:
            messagebox.showerror("Ошибка", "Название и дата обязательны!")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE events SET title = ?, description = ?, date = ?, time = ? WHERE id = ?",
                       (new_title, new_description, new_date, new_time, event_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", "Событие обновлено!")
        edit_window.destroy()
        load_events()

    edit_window = tk.Toplevel(root)
    edit_window.title("Редактировать событие")

    tk.Label(edit_window, text="Название:").grid(row=0, column=0, padx=10, pady=5)
    title_entry = tk.Entry(edit_window, width=30)
    title_entry.insert(0, event[0])
    title_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(edit_window, text="Описание:").grid(row=1, column=0, padx=10, pady=5)
    desc_entry = tk.Text(edit_window, width=30, height=5)
    desc_entry.insert("1.0", event[1])
    desc_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(edit_window, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=5)
    date_entry = tk.Entry(edit_window, width=30)
    date_entry.insert(0, event[2])
    date_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(edit_window, text="Время (HH:MM):").grid(row=3, column=0, padx=10, pady=5)
    time_entry = tk.Entry(edit_window, width=30)
    time_entry.insert(0, event[3])
    time_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Button(edit_window, text="Сохранить изменения", command=save_changes).grid(row=4, column=0, columnspan=2, pady=10)

def search_events():
    search_term = search_entry.get()
    for row in tree.get_children():
        tree.delete(row)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, date, time FROM events WHERE title LIKE ? OR date LIKE ? ORDER BY date, time",
                   ('%' + search_term + '%', '%' + search_term + '%'))
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)
    conn.close()

def check_reminders():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT title, date, time FROM events WHERE date || ' ' || time = ?", (current_time,))
    events = cursor.fetchall()
    conn.close()

    if events:
        for event in events:
            messagebox.showinfo("Напоминание", f"Событие: {event[0]}\nДата и время: {event[1]} {event[2]}")
    
    root.after(60000, check_reminders)

root = tk.Tk()
root.title("Ежедневник")

create_db()

columns = ("ID", "Название", "Дата", "Время")
tree = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(fill=tk.BOTH, expand=True)

btn_frame = tk.Frame(root)
btn_frame.pack(fill=tk.X, pady=10)

tk.Button(btn_frame, text="Добавить событие", command=add_event).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Редактировать событие", command=edit_event).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Удалить событие", command=delete_event).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Обновить", command=load_events).pack(side=tk.LEFT, padx=5)

search_frame = tk.Frame(root)
search_frame.pack(fill=tk.X, pady=10)

tk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, width=30)
search_entry.pack(side=tk.LEFT, padx=5)
tk.Button(search_frame, text="Поиск", command=search_events).pack(side=tk.LEFT, padx=5)

load_events()

check_reminders()

root.mainloop()

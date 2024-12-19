import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

# Создание базы данных и таблиц
def create_db():
    conn = sqlite3.connect("school_diary.db")
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        birth_date TEXT NOT NULL,
        student_class TEXT NOT NULL,
        class_teacher TEXT NOT NULL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        weekday TEXT NOT NULL,
        subjects TEXT
    )
    ''')
    conn.commit()
    conn.close()

def is_student_data_present():
    conn = sqlite3.connect("school_diary.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM student")
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

def save_student_data(full_name, birth_date, student_class, class_teacher):
    conn = sqlite3.connect("school_diary.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO student (full_name, birth_date, student_class, class_teacher) VALUES (?, ?, ?, ?)",
                   (full_name, birth_date, student_class, class_teacher))
    conn.commit()
    conn.close()

def generate_schedule(start_year):
    start_date = datetime(start_year, 9, 1)
    end_date = datetime(start_year + 1, 6, 1)

    conn = sqlite3.connect("school_diary.db")
    cursor = conn.cursor()

    current_date = start_date
    while current_date < end_date:
        if current_date.weekday() < 6:
            cursor.execute("INSERT INTO schedule (date, weekday) VALUES (?, ?)",
                           (current_date.strftime("%Y-%m-%d"), current_date.strftime("%A")))
        current_date += timedelta(days=1)
    conn.commit()
    conn.close()

def student_data_window():
    def save_data():
        full_name = full_name_entry.get()
        birth_date = birth_date_entry.get()
        student_class = class_entry.get()
        class_teacher = teacher_entry.get()

        if not full_name or not birth_date or not student_class or not class_teacher:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return

        save_student_data(full_name, birth_date, student_class, class_teacher)
        generate_schedule(2024)
        student_window.destroy()
        main_window()

    student_window = tk.Tk()
    student_window.title("Данные ученика")

    tk.Label(student_window, text="ФИО ученика:").grid(row=0, column=0, padx=10, pady=5)
    full_name_entry = tk.Entry(student_window, width=30)
    full_name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(student_window, text="Дата рождения (YYYY-MM-DD):").grid(row=1, column=0, padx=10, pady=5)
    birth_date_entry = tk.Entry(student_window, width=30)
    birth_date_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(student_window, text="Класс:").grid(row=2, column=0, padx=10, pady=5)
    class_entry = tk.Entry(student_window, width=30)
    class_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(student_window, text="Классный руководитель:").grid(row=3, column=0, padx=10, pady=5)
    teacher_entry = tk.Entry(student_window, width=30)
    teacher_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Button(student_window, text="Сохранить", command=save_data).grid(row=4, column=0, columnspan=2, pady=10)

    student_window.mainloop()

def main_window():
    def load_schedule():
        for row in tree.get_children():
            tree.delete(row)

        conn = sqlite3.connect("school_diary.db")
        cursor = conn.cursor()
        cursor.execute("SELECT date, weekday, subjects FROM schedule ORDER BY date")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", tk.END, values=row)
        conn.close()

    def edit_schedule():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите дату для редактирования!")
            return

        schedule_id = tree.item(selected_item[0])["values"][0]
        edit_window = tk.Toplevel(root)
        edit_window.title("Редактировать расписание")

        tk.Label(edit_window, text="Предметы (через запятую):").grid(row=0, column=0, padx=10, pady=5)
        subjects_entry = tk.Entry(edit_window, width=50)
        subjects_entry.grid(row=0, column=1, padx=10, pady=5)

        def save_changes():
            subjects = subjects_entry.get()
            conn = sqlite3.connect("school_diary.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE schedule SET subjects = ? WHERE id = ?", (subjects, schedule_id))
            conn.commit()
            conn.close()
            load_schedule()
            edit_window.destroy()

        tk.Button(edit_window, text="Сохранить", command=save_changes).grid(row=1, column=0, columnspan=2, pady=10)

    root = tk.Tk()
    root.title("Школьный дневник")

    columns = ("Дата", "День недели", "Предметы")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill=tk.BOTH, expand=True)

    btn_frame = tk.Frame(root)
    btn_frame.pack(fill=tk.X, pady=10)

    tk.Button(btn_frame, text="Редактировать расписание", command=edit_schedule).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Обновить расписание", command=load_schedule).pack(side=tk.LEFT, padx=5)

    load_schedule()
    root.mainloop()

create_db()
if not is_student_data_present():
    student_data_window()
else:
    main_window()

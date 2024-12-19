import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkhtmlview import HTMLLabel
import tkintermapview
from datetime import datetime, timedelta

def init_db():
    with sqlite3.connect("school_portal.db") as conn:
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS subjects (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            description TEXT)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS teachers (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            full_name TEXT NOT NULL,
                            subject TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS schedule (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            type TEXT NOT NULL,
                            time TEXT NOT NULL,
                            activity TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS classes (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            class_number INTEGER NOT NULL,
                            class_prefix TEXT NOT NULL,
                            student_count INTEGER NOT NULL,
                            class_teacher TEXT NOT NULL)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS textbooks (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            subject TEXT NOT NULL,
                            class_range TEXT NOT NULL,
                            title TEXT NOT NULL,
                            author TEXT NOT NULL)''')

        conn.commit()

        init_data(cursor)
        conn.commit()

def init_data(cursor):
    cursor.execute("DELETE FROM classes")
    
    textbooks_data = [
        ("Математика", "1-4", "Учебник по математике", "С. С. Осипов"),
        ("Математика", "5-9", "Продвинутый учебник по математике", "Т. И. Носкова"),
        ("Физика", "8-11", "Физика для старшеклассников", "Г. А. Кузнецова"),
        ("Химия", "7-9", "Основы химии", "В. И. Петров"),
        ("Биология", "5-8", "Биология для школьников", "Л. П. Григорьева"),
        ("Русский Язык", "5-9", "Учебник по русскому языку", "О. В. Ковалева"),
        ("История", "8-11", "История России", "Д. Н. Лебедев")
    ]

    cursor.execute("DELETE FROM textbooks")
    for textbook in textbooks_data:
        cursor.execute("INSERT INTO textbooks (subject, class_range, title, author) VALUES (?, ?, ?, ?)", textbook)

    teachers_data = [
        ("Иванов Иван Иванович", "Математика"),
        ("Петрова Мария Сергеевна", "Физика"),
        ("Сидоров Алексей Павлович", "Химия"),
        ("Кузнецова Елена Викторовна", "Биология"),
        ("Кузнецова Елена Викторовна", "Химия"),
        ("Золоторева Ирина Сергеевна", "Обществознание"),
        ("Попов Виктор Николаевич", "История"),
        ("Смирнова Татьяна Алексеевна", "География"),
        ("Смирнова Татьяна Алексеевна", "Экономика"),
        ("Васильев Николай Юрьевич", "Физкультура"),
        ("Васильев Николай Юрьевич", "ОБЖ"),
        ("Ковалева Ольга Владимировна", "Литература"),
        ("Ковалева Ольга Владимировна", "Русский Язык"),
        ("Ковалева Ольга Владимировна", "Родной Язык"),
        ("Ковалева Ольга Владимировна", "ИЗО"),
        ("Орлов Сергей Андреевич", "Информатика"),
        ("Беляева Светлана Петровна", "Иностранный язык"),
        ("Борисов Борис Петров", "Иностранный язык"),
        ("Иванов Иван Иванович", "Алгебра"),
        ("Иванов Иван Иванович", "Геометрия"),
        ("Черный Денис Глебович", "Алгебра"),
        ("Черный Денис Глебович", "Геометрия")
    ]

    cursor.execute("DELETE FROM teachers")
    for teacher in teachers_data:
        cursor.execute("INSERT INTO teachers (full_name, subject) VALUES (?, ?)", teacher)

    lesson_start_time = datetime.strptime("09:00", "%H:%M")
    lessons = []
    for i in range(1, 8):
        if i == 5:
            lesson_start_time += timedelta(minutes=40)
        lessons.append((f"{lesson_start_time.strftime('%H:%M')} - {(lesson_start_time + timedelta(minutes=45)).strftime('%H:%M')}", f"{i}-й урок"))
        lesson_start_time += timedelta(minutes=55)

    cursor.execute("DELETE FROM schedule")
    for time, activity in lessons:
        cursor.execute("INSERT INTO schedule (type, time, activity) VALUES (?, ?, ?)", ("lesson", time, activity))

    extra_activities = [
        ("15:00 - 16:00", "Футбольный кружок"),
        ("16:00 - 17:00", "Хор"),
        ("17:00 - 18:00", "Робототехника"),
    ]
    for time, activity in extra_activities:
        cursor.execute("INSERT INTO schedule (type, time, activity) VALUES (?, ?, ?)", ("extra", time, activity))

    classes_data = [
        (1, "А", 25, "Иванов Иван Иванович"),
        (2, "А", 28, "Петрова Мария Сергеевна"),
        (2, "Б", 25, "Золоторева Ирина Сергеевна"),
        (3, "А", 30, "Сидоров Алексей Павлович"),
        (3, "Б", 27, "Сидоров Алексей Павлович"),
        (3, "В", 28, "Черный Денис Глебович"),
        (4, "А", 27, "Кузнецова Елена Викторовна"),
        (5, "А", 29, "Попов Виктор Николаевич"),
        (5, "Б", 26, "Попов Виктор Николаевич"),
        (6, "А", 29, "Смирнова Татьяна Алексеевна"),
        (7, "А", 24, "Васильев Николай Юрьевич"),
        (8, "А", 22, "Борисов Борис Петров"),
        (8, "Б", 22, "Ковалева Ольга Владимировна"),
        (9, "А", 20, "Орлов Сергей Андреевич"),
        (10, "А", 23, "Беляева Светлана Петровна"),
        (11, "А", 21, "Иванов Иван Иванович"),
    ]
    for data in classes_data:
        cursor.execute("INSERT INTO classes (class_number, class_prefix, student_count, class_teacher) VALUES (?, ?, ?, ?)", data)
        
class SchoolPortal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учебный Портал")
        self.geometry("960x560")
        self.init_tabs()

    def init_tabs(self):
        tab_control = ttk.Notebook(self)

        self.teachers_tab = ttk.Frame(tab_control)
        tab_control.add(self.teachers_tab, text="Преподаватели и Персонал")
        self.init_teachers_tab()

        self.classes_tab = ttk.Frame(tab_control)
        tab_control.add(self.classes_tab, text="Классы")
        self.init_classes_tab()
        
        self.textbooks_tab = ttk.Frame(tab_control)
        tab_control.add(self.textbooks_tab, text="Учебники")
        self.init_textbooks_tab()

        self.schedule_tab = ttk.Frame(tab_control)
        tab_control.add(self.schedule_tab, text="Расписание")
        self.init_schedule_tab()

        self.map_tab = ttk.Frame(tab_control)
        tab_control.add(self.map_tab, text="Карта")
        self.init_map_tab()

        tab_control.pack(expand=1, fill="both")

    def init_teachers_tab(self):
        ttk.Label(self.teachers_tab, text="Список преподавателей", font=("Arial", 14)).pack(pady=10)
        self.teachers_listbox = tk.Listbox(self.teachers_tab, width=100, height=20)
        self.teachers_listbox.pack(padx=20, pady=10)

        with sqlite3.connect("school_portal.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT full_name, subject FROM teachers")
            for teacher in cursor.fetchall():
                self.teachers_listbox.insert(tk.END, f"{teacher[0]} - {teacher[1]}")

    def init_schedule_tab(self):
        ttk.Label(self.schedule_tab, text="Расписание уроков и внеурочной деятельности", font=("Arial", 14)).pack(pady=10)

        ttk.Label(self.schedule_tab, text="Расписание уроков:", font=("Arial", 12)).pack(pady=5)
        self.lessons_listbox = tk.Listbox(self.schedule_tab, width=60, height=7)
        self.lessons_listbox.pack(pady=5)

        ttk.Label(self.schedule_tab, text="Расписание внеурочной деятельности:", font=("Arial", 12)).pack(pady=5)
        self.extra_listbox = tk.Listbox(self.schedule_tab, width=60, height=5)
        self.extra_listbox.pack(pady=5)

        with sqlite3.connect("school_portal.db") as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT time, activity FROM schedule WHERE type='lesson'")
            lessons = cursor.fetchall()
            for lesson in lessons:
                self.lessons_listbox.insert(tk.END, f"{lesson[0]} - {lesson[1]}")

            cursor.execute("SELECT time, activity FROM schedule WHERE type='extra'")
            extras = cursor.fetchall()
            for extra in extras:
                self.extra_listbox.insert(tk.END, f"{extra[0]} - {extra[1]}")

    def init_map_tab(self):
        ttk.Label(self.map_tab, text="Местоположение школы", font=("Arial", 14)).pack(pady=10)
        map_widget = tkintermapview.TkinterMapView(self.map_tab, width=800, height=600, corner_radius=0)
        map_widget.pack(fill="both", expand=True)
        map_widget.set_position(52.769622, 41.381247, marker=True)

    def init_classes_tab(self):
        ttk.Label(self.classes_tab, text="Информация о классах", font=("Arial", 14)).pack(pady=10)
        columns = ("ID", "Номер", "Префикс", "Кол-во учеников", "Классный руководитель")

        tree = ttk.Treeview(self.classes_tab, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        tree.pack(fill="both", expand=True)

        with sqlite3.connect("school_portal.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM classes")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)

    def init_textbooks_tab(self):
        ttk.Label(self.textbooks_tab, text="Учебники для классов", font=("Arial", 14)).pack(pady=10)

        columns = ("Предмет", "Классы", "Название", "Автор")

        tree = ttk.Treeview(self.textbooks_tab, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200)

        tree.pack(fill="both", expand=True)

        with sqlite3.connect("school_portal.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subject, class_range, title, author FROM textbooks")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)

if __name__ == "__main__":
    init_db()
    app = SchoolPortal()
    app.mainloop()

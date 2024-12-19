import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime

def connect_db():
    return sqlite3.connect('vacancies.db')

def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        created_by TEXT NOT NULL,
                        position TEXT NOT NULL,
                        specialty TEXT NOT NULL,
                        creation_date TEXT NOT NULL,
                        status TEXT NOT NULL,
                        about TEXT
                    )''')

    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1240x480")
        self.root.title("Управление вакансиями")

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), padding=5)
        style.configure('TButton', font=('Arial', 12), padding=5)
        style.configure('TEntry', font=('Arial', 12), padding=5)
        style.configure('Treeview', font=('Arial', 11), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.create_vacancy_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.create_vacancy_tab, text="Создание вакансии")

        self.vacancy_list_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.vacancy_list_tab, text="Список вакансий")

        self.process_vacancy_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.process_vacancy_tab, text="Обработка вакансий")

        self.create_create_vacancy_tab()
        self.create_vacancy_list_tab()
        self.create_process_vacancy_tab()

    def create_create_vacancy_tab(self):
        frame = ttk.Frame(self.create_vacancy_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Имя создателя:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.entry_created_by = ttk.Entry(frame)
        self.entry_created_by.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Должность:").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.entry_position = ttk.Entry(frame)
        self.entry_position.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Специальность:").grid(row=2, column=0, sticky="W", padx=10, pady=5)
        self.entry_specialty = ttk.Entry(frame)
        self.entry_specialty.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Описание о себе:").grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.entry_about = ttk.Entry(frame)
        self.entry_about.grid(row=3, column=1, padx=10, pady=5)

        ttk.Button(frame, text="Создать вакансию", command=self.create_vacancy).grid(row=4, column=0, columnspan=2, pady=10)

    def create_vacancy(self):
        created_by = self.entry_created_by.get()
        position = self.entry_position.get()
        specialty = self.entry_specialty.get()
        about = self.entry_about.get()

        if created_by and position and specialty:
            conn = connect_db()
            cursor = conn.cursor()
            creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = "Ожидает"

            cursor.execute("INSERT INTO vacancies (created_by, position, specialty, creation_date, status, about) VALUES (?, ?, ?, ?, ?, ?)", 
                           (created_by, position, specialty, creation_date, status, about))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", f"Вакансия на должность '{position}' создана!")
            self.display_vacancies()
            self.load_vacancies_for_processing()
        else:
            messagebox.showerror("Ошибка", "Введите все данные для вакансии!")

    def create_vacancy_list_tab(self):
        frame = ttk.Frame(self.vacancy_list_tab, padding=20)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            frame,
            columns=("ID", "Created By", "Position", "Specialty", "Creation Date", "Status", "About"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Created By", text="Создатель")
        self.tree.heading("Position", text="Должность")
        self.tree.heading("Specialty", text="Специальность")
        self.tree.heading("Creation Date", text="Дата создания")
        self.tree.heading("Status", text="Статус")
        self.tree.heading("About", text="Описание")

        self.tree.pack(fill="both", expand=True, pady=10)

        self.tree.column("ID", width=54, anchor="center")
        self.tree.column("Status", width=96, anchor="w")

        self.display_vacancies()

    def display_vacancies(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''SELECT id, created_by, position, specialty, creation_date, status, about FROM vacancies''')
        vacancies = cursor.fetchall()
        conn.close()

        for vacancy in vacancies:
            self.tree.insert("", "end", values=vacancy)

    def create_process_vacancy_tab(self):
        frame = ttk.Frame(self.process_vacancy_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Выберите вакансию:").grid(row=0, column=0, sticky="W", padx=10, pady=5)

        self.vacancy_combobox = ttk.Combobox(frame, state="readonly")
        self.vacancy_combobox.grid(row=0, column=1, padx=10, pady=5)
        self.vacancy_combobox.bind("<<ComboboxSelected>>", self.show_vacancy_details)

        self.vacancy_details_frame = ttk.Frame(frame)
        self.vacancy_details_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.accept_button = ttk.Button(frame, text="Принять", command=self.accept_vacancy)
        self.accept_button.grid(row=2, column=0, padx=10, pady=10)

        self.reject_button = ttk.Button(frame, text="Отклонить", command=self.reject_vacancy)
        self.reject_button.grid(row=2, column=1, padx=10, pady=10)

        self.load_vacancies_for_processing()

    def load_vacancies_for_processing(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, position FROM vacancies WHERE status = 'Ожидает'")
        vacancies = cursor.fetchall()
        conn.close()

        vacancy_ids = [str(vacancy[0]) for vacancy in vacancies]
        self.vacancy_combobox["values"] = vacancy_ids

    def show_vacancy_details(self, event):
        vacancy_id = self.vacancy_combobox.get()
        if vacancy_id:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT created_by, position, specialty, creation_date, status, about FROM vacancies WHERE id = ?", (vacancy_id,))
            vacancy = cursor.fetchone()
            conn.close()

            for widget in self.vacancy_details_frame.winfo_children():
                widget.destroy()

            if vacancy:
                ttk.Label(self.vacancy_details_frame, text=f"Создатель: {vacancy[0]}").grid(row=0, column=0, sticky="W", padx=10, pady=5)
                ttk.Label(self.vacancy_details_frame, text=f"Должность: {vacancy[1]}").grid(row=1, column=0, sticky="W", padx=10, pady=5)
                ttk.Label(self.vacancy_details_frame, text=f"Специальность: {vacancy[2]}").grid(row=2, column=0, sticky="W", padx=10, pady=5)
                ttk.Label(self.vacancy_details_frame, text=f"Дата создания: {vacancy[3]}").grid(row=3, column=0, sticky="W", padx=10, pady=5)
                ttk.Label(self.vacancy_details_frame, text=f"Статус: {vacancy[4]}").grid(row=4, column=0, sticky="W", padx=10, pady=5)
                ttk.Label(self.vacancy_details_frame, text=f"Описание: {vacancy[5]}").grid(row=5, column=0, sticky="W", padx=10, pady=5)

    def accept_vacancy(self):
        vacancy_id = self.vacancy_combobox.get()
        if vacancy_id:
            self.update_status(vacancy_id, "Принята")
            messagebox.showinfo("Успех", f"Вакансия {vacancy_id} принята!")

    def reject_vacancy(self):
        vacancy_id = self.vacancy_combobox.get()
        if vacancy_id:
            self.update_status(vacancy_id, "Отклонена")
            messagebox.showinfo("Успех", f"Вакансия {vacancy_id} отклонена!")

    def update_status(self, vacancy_id, new_status):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE vacancies SET status = ? WHERE id = ?", (new_status, vacancy_id))
        conn.commit()
        conn.close()
        self.load_vacancies_for_processing()
        self.display_vacancies()

if __name__ == "__main__":
    create_table()
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

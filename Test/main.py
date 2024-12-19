import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import random
import time

DB_NAME = "test_results.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            difficulty TEXT,
            score INTEGER,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

class TestingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система тестирования")
        self.root.geometry("500x400")
        
        self.username = ""
        self.difficulty = ""
        self.questions = []
        self.current_question_index = 0
        self.correct_answers = 0
        self.start_time = 0

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(expand=True, fill="both")

        self.create_main_menu()

    def create_main_menu(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.main_frame, text="Введите ваше имя:", font=("Arial", 14)).pack(pady=10)
        self.name_entry = tk.Entry(self.main_frame, font=("Arial", 14))
        self.name_entry.pack(pady=10)
        
        tk.Label(self.main_frame, text="Выберите уровень сложности:", font=("Arial", 14)).pack(pady=10)
        
        tk.Button(self.main_frame, text="Легкий", font=("Arial", 12), command=lambda: self.start_test("Легкий")).pack(pady=5)
        tk.Button(self.main_frame, text="Средний", font=("Arial", 12), command=lambda: self.start_test("Средний")).pack(pady=5)
        tk.Button(self.main_frame, text="Сложный", font=("Arial", 12), command=lambda: self.start_test("Сложный")).pack(pady=5)
        
        tk.Button(self.main_frame, text="Таблица результатов", font=("Arial", 12), command=self.show_results).pack(pady=20)
    
    def start_test(self, difficulty):
        self.username = self.name_entry.get().strip()
        if not self.username:
            messagebox.showerror("Ошибка", "Пожалуйста, введите ваше имя!")
            return
        
        self.difficulty = difficulty
        self.questions = self.generate_questions(difficulty)
        self.current_question_index = 0
        self.correct_answers = 0
        self.start_time = time.time()
        
        self.show_question()
    
    def generate_questions(self, difficulty):
        base_questions = {
            "Легкий": [
                ("2+2=?", "4"),
                ("3+5=?", "8"),
                ("6-3=?", "3"),
                ("Какая столица Франции?", "Париж"),
                ("Сколько дней в неделе?", "7"),
                ("Кто написал 'Войну и мир'?", "Толстой"),
                ("Какой цвет смешивается с желтым для получения оранжевого?", "Красный"),
                ("Как называется главный город Египта?", "Каир"),
                ("Сколько континентов на Земле?", "7"),
                ("Какая планета самая близкая к Солнцу?", "Меркурий"),
                ("Какой день недели идет после понедельника?", "Вторник"),
                ("Кто открыл закон тяготения?", "Ньютон"),
                ("Какая птица является символом мира?", "Голубь"),
                ("В какой стране находится Великая китайская стена?", "Китай"),
                ("Что получается при смешивании синего и желтого?", "Зеленый"),
                ("Какая валюта используется в Японии?", "Йена"),
                ("Сколько месяцев в году?", "12"),
                ("Что является столицей Великобритании?", "Лондон"),
                ("Кто был первым человеком на Луне?", "Нил Армстронг"),
                ("Какой месяц идет после января?", "Февраль")
            ],
            "Средний": [
                ("Какая планета известна как 'Красная планета'?", "Марс"),
                ("Как называется химический элемент с символом O?", "Кислород"),
                ("Сколько стран в составе Европейского Союза?", "27"),
                ("Какой океан самый большой?", "Тихий океан"),
                ("Из какого металла делают монеты в США?", "Медь"),
                ("Как называется самый высокий водопад в мире?", "Анхель"),
                ("Как называется самый большой остров на Земле?", "Гренландия"),
                ("В каком году началась Вторая мировая война?", "1939"),
                ("Сколько атомов в молекуле воды?", "3"),
                ("Какой элемент периодической таблицы имеет символ Fe?", "Железо"),
                ("Какой газ составляет основную часть атмосферы Земли?", "Азот"),
                ("Какая страна имеет наибольшее количество населения?", "Китай"),
                ("Какое государство первым отправило человека в космос?", "СССР"),
                ("Как называется город, который является столицей Японии?", "Токио"),
                ("Какое животное является самым крупным на планете?", "Синий кит"),
                ("Какая страна является родиной Олимпийских игр?", "Греция"),
                ("Какая единица измерения силы тока?", "Ампер"),
                ("Какое дерево является символом Канады?", "Клен"),
                ("Кто является автором 'Гарри Поттера'?", "Роулинг")
            ],
            "Сложный": [
                ("Кто изобрел телефон?", "Александр Белл"),
                ("Какое химическое соединение является основной частью алмазов?", "Углерод"),
                ("Какое древнегреческое слово означает 'любовь'?", "Эрос"),
                ("Сколько материков на Земле?", "7"),
                ("Какой элемент периодической таблицы имеет атомный номер 79?", "Золото"),
                ("Кто написал 'Мастер и Маргарита'?", "Михаил Булгаков"),
                ("Какой атомный номер у углерода?", "6"),
                ("Какое животное является символом Австралии?", "Кенгуру"),
                ("Какое расстояние до ближайшей звезды (кроме Солнца)?", "4,24 световых года"),
                ("Как называется процесс, при котором растения производят кислород?", "Фотосинтез"),
                ("Как называется самая высокая гора на Земле?", "Эверест"),
                ("В каком году была подписана декларация независимости США?", "1776"),
                ("Какая страна наибольшая по площади?", "Россия"),
                ("Какой элемент в химии обозначается буквой Na?", "Натрий"),
                ("Что такое квантовая физика?", "Область науки, изучающая физические явления на микроскопическом уровне"),
                ("Кто является автором теории относительности?", "Альберт Эйнштейн"),
                ("Какой учёный предложил теорию эволюции?", "Чарльз Дарвин"),
                ("Какой газ является основным компонентом в земной атмосфере?", "Азот"),
                ("Какая река является самой длинной в мире?", "Нил"),
                ("Какой город является столицей Канады?", "Оттава")
            ]
        }
        return random.sample(base_questions[difficulty], len(base_questions[difficulty]))

    def show_question(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        if self.current_question_index < len(self.questions):
            question, _ = self.questions[self.current_question_index]
            tk.Label(self.main_frame, text=question, font=("Arial", 16)).pack(pady=20)
            
            self.answer_entry = tk.Entry(self.main_frame, font=("Arial", 14))
            self.answer_entry.pack(pady=10)
            
            tk.Button(self.main_frame, text="Ответить", font=("Arial", 12), command=self.check_answer).pack(pady=10)
        else:
            self.end_test()

    def check_answer(self):
        user_answer = self.answer_entry.get().strip()
        correct_answer = self.questions[self.current_question_index][1]
        
        if user_answer == correct_answer:
            self.correct_answers += 1
        
        self.current_question_index += 1
        self.show_question()

    def end_test(self):
        end_time = time.time()
        elapsed_time = time.strftime("%M:%S", time.gmtime(end_time - self.start_time))
        score = f"{self.correct_answers}/{len(self.questions)}"
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO results (name, difficulty, score, time) VALUES (?, ?, ?, ?)", 
                       (self.username, self.difficulty, self.correct_answers, elapsed_time))
        conn.commit()
        conn.close()
        
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.main_frame, text=f"Вы ответили на {score} это {int(self.correct_answers / len(self.questions) * 100)}%", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.main_frame, text=f"Вы потратили {elapsed_time} времени", font=("Arial", 14)).pack(pady=10)
        
        tk.Button(self.main_frame, text="Перепройти тест", font=("Arial", 12), command=self.create_main_menu).pack(pady=10)
        tk.Button(self.main_frame, text="Таблица результатов", font=("Arial", 12), command=self.show_results).pack(pady=10)

    def show_results(self):
        results_window = tk.Toplevel(self.root)
        results_window.title("Таблица результатов")
        results_window.geometry("400x300")
        
        tree = ttk.Treeview(results_window, columns=("Name", "Difficulty", "Score", "Time"), show="headings")
        tree.heading("Name", text="Имя")
        tree.heading("Difficulty", text="Сложность")
        tree.heading("Score", text="Результат")
        tree.heading("Time", text="Время")
        tree.pack(expand=True, fill="both")
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT name, difficulty, score, time FROM results ORDER BY time ASC")
        rows = cursor.fetchall()
        for row in rows:
            tree.insert("", "end", values=row)
        conn.close()

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = TestingApp(root)
    root.mainloop()

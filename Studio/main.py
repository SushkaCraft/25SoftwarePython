import tkinter as tk
from tkinter import ttk, messagebox, Listbox, END, PhotoImage
import sqlite3
from tkintermapview import TkinterMapView
from datetime import datetime

def init_db():
    conn = sqlite3.connect("studio.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            review TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date_time TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def add_review():
    name = review_name_entry.get()
    review = review_text_entry.get("1.0", END).strip()
    if not name or not review:
        messagebox.showerror("Ошибка", "Заполните все поля")
        return
    conn = sqlite3.connect("studio.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reviews (name, review) VALUES (?, ?)", (name, review))
    conn.commit()
    conn.close()
    load_reviews()
    review_name_entry.delete(0, END)
    review_text_entry.delete("1.0", END)

def load_reviews():
    reviews_list.delete(0, END)
    conn = sqlite3.connect("studio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, review FROM reviews")
    for name, review in cursor.fetchall():
        reviews_list.insert(END, f"{name}: {review}")
    conn.close()

def book_session():
    name = booking_name_entry.get()
    date_time = booking_datetime_entry.get()
    try:
        datetime.strptime(date_time, "%d-%m-%Y %H:%M")
    except ValueError:
        messagebox.showerror("Ошибка", "Введите дату и время в формате ДД-ММ-ГГГГ ЧЧ:ММ")
        return
    if not name or not date_time:
        messagebox.showerror("Ошибка", "Заполните все поля")
        return
    conn = sqlite3.connect("studio.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bookings (name, date_time) VALUES (?, ?)", (name, date_time))
        conn.commit()
        load_bookings()
        booking_name_entry.delete(0, END)
        booking_datetime_entry.delete(0, END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Ошибка", "Это время уже занято")
    conn.close()

def load_bookings():
    bookings_list.delete(0, END)
    conn = sqlite3.connect("studio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, date_time FROM bookings")
    for name, date_time in cursor.fetchall():
        bookings_list.insert(END, f"{name} - {date_time}")
    conn.close()

init_db()

root = tk.Tk()
root.title("Студия звукозаписи")
root.geometry("960x400")
root.minsize(width=960, height=380)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

frame_description = ttk.Frame(notebook)
notebook.add(frame_description, text="Описание студии")

title_label =  tk.Label(frame_description, text="КОРОТКО О НАС", font=("Arial", 12, 'bold'), justify="center")

description_label = tk.Label(frame_description, text="""Добро пожаловать в нашу студию звукозаписи!\nЗдесь вы найдете лучшее оборудование и профессиональный подход.\nАудио оформление вашего проекта
- озвучка видео
- аудиоролики
- минусовка по референсу
- playback для кавер-групп
- аранжировка
- запись, сведение, мастеринг
- beatmaking
- написание музыки

Мы гарантируем высочайшее качество в каждом проекте.
Наши профессиональные инженеры всегда готовы помочь вам с любыми задачами.
Не стесняйтесь обращаться за консультацией!""", font=("Arial", 12), justify="left")

image = tk.PhotoImage(file="logo.png")
image = image.subsample(28, 28)
image_label = tk.Label(frame_description, image=image)

title_label.pack(side="top", padx=24, pady=8, anchor="c")
description_label.pack(side="left", padx=24, pady=8, anchor="w", fill="x")
image_label.pack(side="right", padx=16, pady=8)

frame_reviews = ttk.Frame(notebook)
notebook.add(frame_reviews, text="Отзывы")
review_name_label = tk.Label(frame_reviews, text="Ваше имя:")
review_name_label.pack()
review_name_entry = tk.Entry(frame_reviews)
review_name_entry.pack()
review_text_label = tk.Label(frame_reviews, text="Ваш отзыв:")
review_text_label.pack()
review_text_entry = tk.Text(frame_reviews, height=5)
review_text_entry.pack()
review_submit_button = tk.Button(frame_reviews, text="Оставить отзыв", command=add_review)
review_submit_button.pack()
reviews_list = Listbox(frame_reviews, width=80, height=10)
reviews_list.pack(padx=10, pady=10)
load_reviews()

frame_equipment = ttk.Frame(notebook)
notebook.add(frame_equipment, text="Оборудование")
equipment_label = tk.Label(frame_equipment, text="Наше оборудование:\n- Микрофоны: Neumann U87, Shure SM7B\n- Аудиоинтерфейсы: Apollo Twin X\n- Мониторы: Yamaha HS8\n- Программы: Pro Tools, Logic Pro X", font=("Arial", 12))
equipment_label.pack(padx=10, pady=10)

frame_booking = ttk.Frame(notebook)
notebook.add(frame_booking, text="Записаться на запись")
booking_name_label = tk.Label(frame_booking, text="Имя:")
booking_name_label.grid(row=0, column=0, padx=5, pady=5)
booking_name_entry = tk.Entry(frame_booking)
booking_name_entry.grid(row=0, column=1, padx=5, pady=5)
booking_datetime_label = tk.Label(frame_booking, text="Дата и время (ДД-ММ-ГГГГ ЧЧ:ММ):")
booking_datetime_label.grid(row=1, column=0, padx=5, pady=5)
booking_datetime_entry = tk.Entry(frame_booking)
booking_datetime_entry.grid(row=1, column=1, padx=5, pady=5)
booking_submit_button = tk.Button(frame_booking, text="Записаться", command=book_session)
booking_submit_button.grid(row=2, column=0, columnspan=2, pady=10)
bookings_list = Listbox(frame_booking, width=50, height=10)
bookings_list.grid(row=0, column=2, rowspan=3, padx=10, pady=10)
load_bookings()

frame_map = ttk.Frame(notebook)
notebook.add(frame_map, text="Студия на карте")
map_widget = TkinterMapView(frame_map, width=800, height=600)
map_widget.pack(fill="both", expand=True)
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=48)
map_widget.set_position(52.75083630847106, 41.45019037631771, marker=True)

root.mainloop()

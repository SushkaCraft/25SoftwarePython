import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta

def connect_db():
    return sqlite3.connect('tickets.db')

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transport_type TEXT NOT NULL,
                        from_location TEXT NOT NULL,
                        to_location TEXT NOT NULL,
                        departure_time TEXT NOT NULL,
                        arrival_time TEXT NOT NULL,
                        date TEXT NOT NULL,
                        seat TEXT NOT NULL,
                        price REAL NOT NULL,
                        available_seats INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1080x540")
        self.root.title("Бронирование билетов")

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), padding=5)
        style.configure('TButton', font=('Arial', 12), padding=5)
        style.configure('TEntry', font=('Arial', 12), padding=5)
        style.configure('Treeview', font=('Arial', 11), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.management_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.management_tab, text="Управление билетами")

        self.available_tickets_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.available_tickets_tab, text="Доступные билеты")

        self.create_management_tab()
        self.create_available_tickets_tab()
        self.create_booking_tab()

    def create_management_tab(self):
        frame = ttk.Frame(self.management_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Тип транспорта:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.transport_type = ttk.Combobox(frame, values=["Самолет", "Поезд", "Автобус"])
        self.transport_type.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Откуда:").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.entry_from = ttk.Entry(frame)
        self.entry_from.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Куда:").grid(row=2, column=0, sticky="W", padx=10, pady=5)
        self.entry_to = ttk.Entry(frame)
        self.entry_to.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Время отправления:").grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.entry_departure_time = ttk.Entry(frame)
        self.entry_departure_time.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Время прибытия:").grid(row=4, column=0, sticky="W", padx=10, pady=5)
        self.entry_arrival_time = ttk.Entry(frame)
        self.entry_arrival_time.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Дата:").grid(row=5, column=0, sticky="W", padx=10, pady=5)
        self.entry_date = ttk.Entry(frame)
        self.entry_date.grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Место:").grid(row=6, column=0, sticky="W", padx=10, pady=5)
        self.entry_seat = ttk.Entry(frame)
        self.entry_seat.grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Цена:").grid(row=7, column=0, sticky="W", padx=10, pady=5)
        self.entry_price = ttk.Entry(frame)
        self.entry_price.grid(row=7, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Доступно мест:").grid(row=8, column=0, sticky="W", padx=10, pady=5)
        self.entry_available_seats = ttk.Entry(frame)
        self.entry_available_seats.grid(row=8, column=1, padx=10, pady=5)

        ttk.Button(frame, text="Добавить билет", command=self.add_ticket).grid(row=9, column=0, columnspan=2, pady=10)

    def create_booking_tab(self):
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="Бронирование билетов")

        ttk.Label(frame, text="Выберите билет:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.ticket_combobox = ttk.Combobox(frame)
        self.ticket_combobox.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Информация о билете:").grid(row=1, column=0, columnspan=2, sticky="W", padx=10, pady=5)
        self.ticket_info = ttk.Label(frame, text="", relief="sunken", anchor="w")
        self.ticket_info.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="Количество билетов:").grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.ticket_quantity = ttk.Entry(frame)
        self.ticket_quantity.grid(row=3, column=1, padx=10, pady=5)

        ttk.Button(frame, text="Забронировать", command=self.book_selected_ticket).grid(row=4, column=0, columnspan=2, pady=10)

        self.update_ticket_combobox()

    def create_booking_tab(self):
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="Бронирование билетов")

        ttk.Label(frame, text="Выберите билет:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.ticket_combobox = ttk.Combobox(frame)
        self.ticket_combobox.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Информация о билете:").grid(row=1, column=0, columnspan=2, sticky="W", padx=10, pady=5)
        self.ticket_info = ttk.Label(frame, text="", relief="sunken", anchor="w")
        self.ticket_info.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="Количество билетов:").grid(row=3, column=0, sticky="W", padx=10, pady=5)
        self.ticket_quantity = ttk.Entry(frame)
        self.ticket_quantity.grid(row=3, column=1, padx=10, pady=5)

        ttk.Button(frame, text="Забронировать", command=self.book_selected_ticket).grid(row=4, column=0, columnspan=2, pady=10)

        self.update_ticket_combobox()
        
        self.ticket_combobox.bind("<<ComboboxSelected>>", self.update_ticket_info)

    def add_ticket(self):
        transport_type = self.transport_type.get()
        from_location = self.entry_from.get()
        to_location = self.entry_to.get()
        departure_time = self.entry_departure_time.get()
        arrival_time = self.entry_arrival_time.get()
        date = self.entry_date.get()
        seat = self.entry_seat.get()
        price = self.entry_price.get()
        available_seats = self.entry_available_seats.get()

        if transport_type and from_location and to_location and departure_time and arrival_time and date and seat and price and available_seats:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO tickets (transport_type, from_location, to_location, 
                                                    departure_time, arrival_time, date, seat, price, available_seats) 
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                           (transport_type, from_location, to_location, departure_time, arrival_time, date, seat, float(price), int(available_seats)))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Билет добавлен!")
            self.display_available_tickets()
        else:
            messagebox.showerror("Ошибка", "Заполните все поля!")

    def update_ticket_combobox(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, departure_time, transport_type FROM tickets")
        tickets = cursor.fetchall()
        conn.close()
        self.ticket_combobox['values'] = [f"{t[0]}-{t[1]}-{t[2]}-{t[3]}" for t in tickets]

    def update_ticket_info(self, event=None):
        selected = self.ticket_combobox.get()
        if selected:
            ticket_id = int(selected.split('-')[0])
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT transport_type, from_location, to_location, departure_time, arrival_time, date, seat, price, available_seats FROM tickets WHERE id = ?", (ticket_id,))
            ticket = cursor.fetchone()
            conn.close()

            if ticket:
                info = f"Тип транспорта: {ticket[0]}\n"
                info += f"Откуда: {ticket[1]}\n"
                info += f"Куда: {ticket[2]}\n"
                info += f"Время отправления: {ticket[3]}\n"
                info += f"Время прибытия: {ticket[4]}\n"
                info += f"Дата: {ticket[5]}\n"
                info += f"Место: {ticket[6]}\n"
                info += f"Цена: {ticket[7]} руб.\n"
                info += f"Доступно мест: {ticket[8]}"
                self.ticket_info.config(text=info)

    def book_selected_ticket(self):
        selected = self.ticket_combobox.get()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите билет!")
            return

        ticket_id = int(selected.split('-')[0])
        quantity = self.ticket_quantity.get()
        if not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showerror("Ошибка", "Введите корректное количество билетов!")
            return

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT available_seats, price FROM tickets WHERE id = ?", (ticket_id,))
        ticket = cursor.fetchone()
        if ticket and ticket[0] >= int(quantity):
            total_price = ticket[1] * int(quantity)
            cursor.execute("UPDATE tickets SET available_seats = available_seats - ? WHERE id = ?", (int(quantity), ticket_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", f"Бронирование успешно! Общая стоимость: {total_price} руб.")
            self.update_ticket_combobox()
        else:
            messagebox.showerror("Ошибка", "Недостаточно доступных мест!")

    def create_available_tickets_tab(self):
        frame = ttk.Frame(self.available_tickets_tab, padding=20)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            frame,
            columns=("ID", "Transport Type", "From", "To", "Departure Time", "Arrival Time", "Date", "Seat", "Price", "Available Seats"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Transport Type", text="Тип транспорта")
        self.tree.heading("From", text="Откуда")
        self.tree.heading("To", text="Куда")
        self.tree.heading("Departure Time", text="Время отправления")
        self.tree.heading("Arrival Time", text="Время прибытия")
        self.tree.heading("Date", text="Дата")
        self.tree.heading("Seat", text="Место")
        self.tree.heading("Price", text="Цена")
        self.tree.heading("Available Seats", text="Доступно мест")

        self.tree.pack(fill="both", expand=True, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="Удалить билет", command=self.delete_ticket).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Обновить информацию", command=self.display_available_tickets).pack(side="left", padx=5)

        self.display_available_tickets()

    def delete_ticket(self):
        selected_item = self.tree.selection()
        if selected_item:
            ticket_id = self.tree.item(selected_item)["values"][0]
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            conn.commit()
            conn.close()
            self.display_available_tickets()
            messagebox.showinfo("Успех", "Билет удален!")
        else:
            messagebox.showerror("Ошибка", "Выберите билет для удаления!")

    def display_available_tickets(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tickets WHERE available_seats > 0")
        tickets = cursor.fetchall()
        conn.close()

        for ticket in tickets:
            self.tree.insert("", "end", values=(ticket[0], ticket[1], ticket[2], ticket[3], ticket[4], ticket[5], ticket[6], ticket[7], ticket[8], ticket[9]))

if __name__ == "__main__":
    root = tk.Tk()
    create_table()
    app = AppGUI(root)
    root.mainloop()

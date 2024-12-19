import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from datetime import datetime, timedelta

def connect_db():
    return sqlite3.connect('library.db')

def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        borrowed_by TEXT,
                        borrow_date TEXT)''')
    conn.commit()
    conn.close()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1080x480")
        self.root.title("Управление библиотекой")

        create_table()

        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 12), padding=5)
        style.configure('TButton', font=('Arial', 12), padding=5)
        style.configure('TEntry', font=('Arial', 12), padding=5)
        style.configure('Treeview', font=('Arial', 11), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        self.management_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.management_tab, text="Управление")

        self.knowledge_base_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.knowledge_base_tab, text="База знаний")

        self.create_management_tab()
        self.create_knowledge_base_tab()

    def create_management_tab(self):
        frame = ttk.Frame(self.management_tab, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Название книги:").grid(row=0, column=0, sticky="W", padx=10, pady=5)
        self.entry_title = ttk.Entry(frame)
        self.entry_title.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Автор книги:").grid(row=1, column=0, sticky="W", padx=10, pady=5)
        self.entry_author = ttk.Entry(frame)
        self.entry_author.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(frame, text="Имя заемщика:").grid(row=2, column=0, sticky="W", padx=10, pady=5)
        self.entry_borrower = ttk.Entry(frame)
        self.entry_borrower.grid(row=2, column=1, padx=10, pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Добавить книгу", command=self.add_book).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Взять книгу", command=self.borrow_book).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Вернуть книгу", command=self.return_book).pack(side="left", padx=5)

    def create_knowledge_base_tab(self):
        frame = ttk.Frame(self.knowledge_base_tab, padding=20)
        frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            frame,
            columns=("ID", "Title", "Author", "Borrowed By", "Return Date"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Название")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Borrowed By", text="Кто взял")
        self.tree.heading("Return Date", text="Дата возврата")

        self.tree.pack(fill="both", expand=True, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="Удалить книгу", command=self.delete_book).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Обновить информацию", command=self.display_books_knowledge_base).pack(side="left", padx=5)

        self.display_books_knowledge_base()
        
    def add_book(self):
        title = self.entry_title.get()
        author = self.entry_author.get()
        if title and author:
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Книга добавлена!")
            self.display_books_knowledge_base()
        else:
            messagebox.showerror("Ошибка", "Введите название и автора книги!")

    def delete_book(self):
        selected_item = self.tree.selection()
        if selected_item:
            book_id = self.tree.item(selected_item)["values"][0]
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            conn.commit()
            conn.close()
            self.display_books_knowledge_base()
            messagebox.showinfo("Успех", "Книга удалена!")
        else:
            messagebox.showerror("Ошибка", "Выберите книгу для удаления!")

    def display_books_knowledge_base(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        conn.close()

        for book in books:
            borrowed_info = "Нет"
            return_date = "Не указано"
            if book[3]:
                borrow_date = datetime.strptime(book[4], "%Y-%m-%d %H:%M:%S")
                return_date = borrow_date + timedelta(days=14)
                borrowed_info = f"Взята: {book[3]}"
            self.tree.insert("", "end", values=(book[0], book[1], book[2], borrowed_info, return_date))

    def borrow_book(self):
        book_identifier = self.entry_title.get()
        borrower = self.entry_borrower.get()

        if not book_identifier or not borrower:
            messagebox.showerror("Ошибка", "Введите ID или название книги и имя заемщика!")
            return

        conn = connect_db()
        cursor = conn.cursor()

        if book_identifier.isdigit():
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_identifier,))
        else:
            cursor.execute("SELECT * FROM books WHERE title = ?", (book_identifier,))
        book = cursor.fetchone()

        if not book:
            messagebox.showerror("Ошибка", "Книга с таким ID или названием не найдена!")
            conn.close()
            return

        if book[3] is not None:
            messagebox.showerror("Ошибка", f"Книга '{book[1]}' уже взята {book[3]}!")
            conn.close()
            return

        cursor.execute("UPDATE books SET borrowed_by = ?, borrow_date = ? WHERE id = ?", 
                    (borrower, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), book[0]))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", f"Книга '{book[1]}' успешно взята {borrower}!")
        self.display_books_knowledge_base()

    def return_book(self):
        book_identifier = self.entry_title.get()

        if not book_identifier:
            messagebox.showerror("Ошибка", "Введите ID или название книги для возврата!")
            return

        conn = connect_db()
        cursor = conn.cursor()

        if book_identifier.isdigit():
            cursor.execute("SELECT * FROM books WHERE id = ?", (book_identifier,))
        else:
            cursor.execute("SELECT * FROM books WHERE title = ?", (book_identifier,))
        book = cursor.fetchone()

        if not book:
            messagebox.showerror("Ошибка", "Книга с таким ID или названием не найдена!")
            conn.close()
            return

        if book[3] is None:
            messagebox.showerror("Ошибка", f"Книга '{book[1]}' не была взята!")
            conn.close()
            return

        cursor.execute("UPDATE books SET borrowed_by = NULL, borrow_date = NULL WHERE id = ?", (book[0],))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", f"Книга '{book[1]}' успешно возвращена!")
        self.display_books_knowledge_base()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

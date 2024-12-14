import tkinter as tk
from tkinter import simpledialog, messagebox
import requests
import json
import os
from threading import Thread

class MessengerApp:
    def __init__(self, root, username):
        self.root = root
        self.root.title("Мессенджер")
        self.root.geometry("340x380")
        
        self.username = username

        self.chat_display = tk.Text(self.root, state="disabled", width=50, height=20)
        self.chat_display.pack(pady=10)
        
        self.message_entry = tk.Entry(self.root, width=40)
        self.message_entry.pack(side="left", padx=5)
        self.message_entry.bind("<Return>", self.send_message)
        
        self.send_button = tk.Button(self.root, text="Отправить", command=self.send_message)
        self.send_button.pack(side="right", padx=5)

        self.last_message_count = 0
        self.load_messages()

        self.update_chat()

    def send_message(self, event=None):
        message = self.message_entry.get().strip()
        if message:
            try:
                response = requests.post('http://127.0.0.1:5000/send_message', json={
                    'username': self.username,
                    'message': message
                })
                if response.status_code == 200:
                    self.display_message(f"{self.username}: {message}")
                    self.message_entry.delete(0, tk.END)
                    self.load_messages()
                else:
                    messagebox.showerror("Ошибка", "Не удалось отправить сообщение.")
            except requests.exceptions.RequestException:
                messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")

    def display_message(self, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, message + "\n")
        self.chat_display.config(state="disabled")
        self.chat_display.see(tk.END)

    def load_messages(self):
        """Загружаем историю сообщений с сервера"""
        try:
            response = requests.get('http://127.0.0.1:5000/get_history')
            if response.status_code == 200:
                messages = response.json().get("history", [])
                self.chat_display.config(state="normal")
                self.chat_display.delete(1.0, tk.END)
                for msg in messages:
                    self.display_message(f"{msg['username']}: {msg['message']}")
                self.chat_display.config(state="disabled")
                self.last_message_count = len(messages)
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается загрузить историю сообщений.")

    def update_chat(self):
        """Периодически проверяем наличие новых сообщений и обновляем чат"""
        try:
            response = requests.get('http://127.0.0.1:5000/get_history')
            if response.status_code == 200:
                messages = response.json().get("history", [])
                if len(messages) > self.last_message_count:
                    for msg in messages[self.last_message_count:]:
                        self.display_message(f"{msg['username']}: {msg['message']}")
                    self.last_message_count = len(messages)
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается проверить новые сообщения.")

        self.root.after(2000, self.update_chat)

def start_messenger():
    root = tk.Tk()
    root.withdraw()

    username = simpledialog.askstring("Имя пользователя", "Введите ваше имя:", initialvalue="Аноним")
    if not username:
        username = "Аноним"
    
    root.deiconify()
    app = MessengerApp(root, username)
    root.mainloop()

if __name__ == "__main__":
    start_messenger()

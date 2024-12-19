import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import requests
from datetime import datetime

class AuctionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Аукцион")
        self.root.geometry("800x600")

        self.username = simpledialog.askstring("Имя пользователя", "Введите ваше имя:")
        if not self.username:
            self.username = "Аноним"

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.create_lot_frame = tk.Frame(self.notebook)
        self.purchase_lot_frame = tk.Frame(self.notebook)
        self.history_frame = tk.Frame(self.notebook)

        self.notebook.add(self.create_lot_frame, text="Создать лот")
        self.notebook.add(self.purchase_lot_frame, text="Приобрести лот")
        self.notebook.add(self.history_frame, text="История лотов")

        self.setup_create_lot_tab()
        self.setup_purchase_lot_tab()
        self.setup_history_tab()
        self.update_purchase_tab()

    def setup_create_lot_tab(self):
        tk.Label(self.create_lot_frame, text="Название лота:").grid(row=0, column=0, padx=5, pady=5)
        self.lot_name_entry = tk.Entry(self.create_lot_frame)
        self.lot_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.create_lot_frame, text="Владелец лота:").grid(row=1, column=0, padx=5, pady=5)
        self.lot_owner_entry = tk.Entry(self.create_lot_frame)
        self.lot_owner_entry.insert(0, self.username)
        self.lot_owner_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.create_lot_frame, text="Начальная цена:").grid(row=2, column=0, padx=5, pady=5)
        self.start_price_entry = tk.Entry(self.create_lot_frame)
        self.start_price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.create_lot_frame, text="Минимальный шаг ставки:").grid(row=3, column=0, padx=5, pady=5)
        self.min_step_entry = tk.Entry(self.create_lot_frame)
        self.min_step_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.create_lot_frame, text="Описание лота:").grid(row=4, column=0, padx=5, pady=5)
        self.lot_description_entry = tk.Entry(self.create_lot_frame)
        self.lot_description_entry.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(self.create_lot_frame, text="Время окончания (ГГГГ-ММ-ДД ЧЧ:ММ):").grid(row=5, column=0, padx=5, pady=5)
        self.end_time_entry = tk.Entry(self.create_lot_frame)
        self.end_time_entry.grid(row=5, column=1, padx=5, pady=5)

        create_button = tk.Button(self.create_lot_frame, text="Создать", command=self.create_lot)
        create_button.grid(row=6, column=1, pady=10)

    def setup_purchase_lot_tab(self):
        tk.Label(self.purchase_lot_frame, text="Выберите лот:").pack(pady=5)
        self.lot_selector = ttk.Combobox(self.purchase_lot_frame)
        self.lot_selector.pack(pady=5)

        self.lot_info_label = tk.Label(self.purchase_lot_frame, text="Информация о лоте")
        self.lot_info_label.pack(pady=5)

        tk.Label(self.purchase_lot_frame, text="Поднять ставку до:").pack(pady=5)
        self.bid_entry = tk.Entry(self.purchase_lot_frame)
        self.bid_entry.pack(pady=5)

        bid_button = tk.Button(self.purchase_lot_frame, text="Сделать ставку", command=self.place_bid)
        bid_button.pack(pady=10)
        self.lot_selector.bind("<<ComboboxSelected>>", self.on_lot_selected)

        self.update_purchase_tab()

    def on_lot_selected(self, event):
        try:
            response = requests.get("http://127.0.0.1:5000/get_lots")
            if response.status_code == 200:
                lots = response.json().get("lots", [])
                selected_lot_id = int(self.lot_selector.get().split(":")[0])
                selected_lot = next(lot for lot in lots if lot['id'] == selected_lot_id)
                self.lot_info_label["text"] = (f"Название: {selected_lot['name']}\n"
                                              f"Описание: {selected_lot['description']}\n"
                                              f"Текущая цена: {selected_lot['current_price']}\n"
                                              f"Владелец: {selected_lot['owner']}\n"
                                              f"Минимальный шаг: {selected_lot['min_step']}\n"
                                              f"Время окончания: {selected_lot['end_time']}")
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")

    def setup_history_tab(self):
        self.history_tree = ttk.Treeview(self.history_frame, columns=("id", "name", "description", "owner", "created", "end", "current_price", "min_step"), show="headings")
        self.history_tree.pack(fill="both", expand=True)

        for col in self.history_tree["columns"]:
            self.history_tree.heading(col, text=col.capitalize())
            self.history_tree.column(col, width=100)

        self.update_history_tab()

    def create_lot(self):
        data = {
            "name": self.lot_name_entry.get(),
            "owner": self.lot_owner_entry.get(),
            "start_price": float(self.start_price_entry.get()),
            "min_step": float(self.min_step_entry.get()),
            "description": self.lot_description_entry.get(),
            "end_time": self.end_time_entry.get()
        }

        try:
            response = requests.post("http://127.0.0.1:5000/create_lot", json=data)
            if response.status_code == 200:
                messagebox.showinfo("Успех", "Лот создан успешно!")
                self.update_purchase_tab()
                self.update_history_tab()
            else:
                messagebox.showerror("Ошибка", response.json().get("error", "Не удалось создать лот."))
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")
        
        self.update_purchase_tab()

    def update_purchase_tab(self):
        try:
            response = requests.get("http://127.0.0.1:5000/get_lots")
            if response.status_code == 200:
                lots = response.json().get("lots", [])
                self.lot_selector["values"] = [
                    f"{lot['id']}: {lot['name']}" 
                    for lot in lots 
                    if not lot.get('winner')
                ]
                if lots:
                    self.lot_selector.set(self.lot_selector["values"][0])
                else:
                    self.lot_selector.set('')
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить лоты.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")

    def place_bid(self):
        if not self.lot_selector.get():
            messagebox.showerror("Ошибка", "Выберите лот для ставки.")
            return

        lot_id = int(self.lot_selector.get().split(":")[0])
        bid_amount = float(self.bid_entry.get())

        try:
            response = requests.post("http://127.0.0.1:5000/place_bid", json={"lot_id": lot_id, "bidder": self.username, "amount": bid_amount})
            if response.status_code == 200:
                messagebox.showinfo("Успех", "Ставка сделана успешно!")
                self.update_purchase_tab()
                self.update_history_tab()
            else:
                messagebox.showerror("Ошибка", response.json().get("error", "Не удалось сделать ставку."))
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")

    def update_history_tab(self):
        try:
            response = requests.get("http://127.0.0.1:5000/get_lots")
            if response.status_code == 200:
                lots = response.json().get("lots", [])
                print(lots)
                for row in self.history_tree.get_children():
                    self.history_tree.delete(row)
                for lot in lots:
                    self.history_tree.insert("", "end", values=(
                        lot.get("id"), lot.get("name"), lot.get("description"), lot.get("owner"),
                        lot.get("created"), lot.get("end_time"), lot.get("current_price"), lot.get("min_step")
                    ))
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить историю лотов.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AuctionApp(root)
    root.mainloop()

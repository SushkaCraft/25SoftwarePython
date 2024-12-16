import tkinter as tk
from tkinter import simpledialog, messagebox
import requests
from datetime import datetime

class AuctionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Аукцион")
        self.root.geometry("600x400")

        self.username = simpledialog.askstring("Имя пользователя", "Введите ваше имя:")
        if not self.username:
            self.username = "Аноним"

        self.lots_frame = tk.Frame(self.root)
        self.lots_frame.pack(fill="both", expand=True)

        self.update_lots()

    def update_lots(self):
        try:
            response = requests.get('http://127.0.0.1:5000/get_lots')
            if response.status_code == 200:
                lots = response.json().get("lots", [])
                self.display_lots(lots)
            else:
                messagebox.showerror("Ошибка", "Не удалось загрузить лоты.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")

        self.root.after(2000, self.update_lots)

    def display_lots(self, lots):
        for widget in self.lots_frame.winfo_children():
            widget.destroy()

        for lot in lots:
            frame = tk.Frame(self.lots_frame, borderwidth=1, relief="solid", padx=10, pady=10)
            frame.pack(pady=5, fill="x")

            tk.Label(frame, text=f"Лот: {lot[1]}").pack(anchor="w")
            tk.Label(frame, text=f"Описание: {lot[2]}").pack(anchor="w")
            tk.Label(frame, text=f"Текущая цена: {lot[4]}").pack(anchor="w")
            tk.Label(frame, text=f"Окончание: {lot[5]}").pack(anchor="w")

            bid_button = tk.Button(frame, text="Сделать ставку", command=lambda l=lot: self.place_bid(l))
            bid_button.pack(anchor="e")

    def place_bid(self, lot):
        bid_amount = simpledialog.askfloat("Ставка", f"Введите вашу ставку (текущая цена: {lot[4]}):")
        if bid_amount and bid_amount > lot[4]:
            try:
                response = requests.post('http://127.0.0.1:5000/place_bid', json={
                    "lot_id": lot[0],
                    "bidder": self.username,
                    "amount": bid_amount
                })
                if response.status_code == 200:
                    messagebox.showinfo("Успех", "Ставка успешно сделана!")
                    self.update_lots()
                else:
                    messagebox.showerror("Ошибка", response.json().get("error", "Не удалось сделать ставку."))
            except requests.exceptions.RequestException:
                messagebox.showerror("Ошибка", "Не удается подключиться к серверу.")
        else:
            messagebox.showerror("Ошибка", "Ставка должна быть выше текущей цены.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AuctionApp(root)
    root.mainloop()

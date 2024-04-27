import tkinter as tk
from tkinter import ttk

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1280x720")
        self.title("FTP Client")

        tk.Label(self, text="Welcome to the FTP Client!").pack()

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("1280x720")  # Установка размера окна
        self.title("FTP Client - Login")  # Установка заголовка окна

        # Создание меток и полей ввода
        tk.Label(self, text="Host:").pack()
        self.host_entry = tk.Entry(self)
        self.host_entry.pack()

        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Label(self, text="Port:").pack()
        self.port_entry = tk.Entry(self)
        self.port_entry.pack()

        # Создание кнопки входа
        self.login_button = ttk.Button(self, text="Login", command=self.login)
        self.login_button.pack()

    def login(self):
        # Получение данных из полей ввода
        host = self.host_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        port = self.port_entry.get()

        # Здесь вы можете добавить код для входа в систему
        print(f"Host: {host}, Username: {username}, Password: {password}, Port: {port}")

        # Если вход успешный, закрыть окно входа и открыть главное окно
        self.destroy()
        MainWindow().mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно

    login_window = LoginWindow(root)

    root.mainloop()
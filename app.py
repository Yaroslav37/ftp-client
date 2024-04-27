import tkinter as tk
from tkinter import ttk
from ftplib import FTP
import tkinter.messagebox

class FTPClient:
    def __init__(self, host, port, username, password):
        self.ftp = FTP()
        self.ftp.connect(host, int(port))
        self.ftp.login(username, password)

    def change_directory(self, path):
        self.ftp.cwd(path)

    def list_files(self):
        return self.ftp.nlst()

    def get_current_directory(self):
        return self.ftp.pwd()

    def download_file(self, filename, local_filename=None):
        if local_filename is None:
            local_filename = filename

        with open(local_filename, 'wb') as f:
            self.ftp.retrbinary('RETR ' + filename, f.write)

    def upload_file(self, filename, local_filename=None):
        if local_filename is None:
            local_filename = filename

        with open(local_filename, 'rb') as f:
            self.ftp.storbinary('STOR ' + filename, f)

    def close(self):
        self.ftp.quit()

class MainWindow(tk.Tk):
    def __init__(self, ftp_client):
        super().__init__()

        self.geometry("1280x720")
        self.title("FTP Client")

        self.ftp_client = ftp_client

        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH, expand=1)

        self.populate_tree()

    def populate_tree(self):
        files = self.ftp_client.list_files()

        for file in files:
            self.tree.insert('', 'end', text=file)

    def on_close(self):
        self.ftp_client.close()
        self.destroy()

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("1280x720")  # Установка размера окна
        self.title("FTP Client - Login")  # Установка заголовка окна

        # Создание меток и полей ввода
        tk.Label(self, text="Host:").grid(row=0, column=0, sticky="e")
        self.host_entry = tk.Entry(self)
        self.host_entry.grid(row=0, column=1)
        self.host_entry.insert(0, "test.rebex.net")

        tk.Label(self, text="Username:").grid(row=1, column=0, sticky="e")
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=1, column=1)
        self.username_entry.insert(0, "demo")

        tk.Label(self, text="Password:").grid(row=2, column=0, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=2, column=1)
        self.password_entry.insert(0, "password")

        tk.Label(self, text="Port:").grid(row=3, column=0, sticky="e")
        self.port_entry = tk.Entry(self)
        self.port_entry.grid(row=3, column=1)
        self.port_entry.insert(0, "21")

        # Создание кнопки входа
        self.login_button = ttk.Button(self, text="Login", command=self.login)
        self.login_button.grid(row=4, column=0, columnspan=2)

    def login(self):
        # Получение данных из полей ввода
        host = self.host_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        port = self.port_entry.get()

        # Создание объекта FTP и попытка подключения
        try:
            ftp_client = FTPClient(host, port, username, password)
            print("Login successful")
            # Если вход успешный, закрыть окно входа и открыть главное окно
            self.destroy()
            main_window = MainWindow(ftp_client)
            main_window.protocol("WM_DELETE_WINDOW", main_window.on_close)
            main_window.mainloop()
        except Exception as e:
            print(f"Failed to login: {e}")
            tkinter.messagebox.showerror("Login Error", f"Failed to login: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно

    login_window = LoginWindow(root)

    root.mainloop()
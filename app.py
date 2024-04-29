import tkinter as tk
from tkinter import ttk
from ftplib import FTP
import tkinter.messagebox
import tkinter.filedialog
import os
import io

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

    def download_file(self, filename, download_dir):
        local_filename = os.path.join(download_dir, filename)  # Создание полного пути к файлу на локальном компьютере

        with open(local_filename, 'wb') as f:
            self.ftp.retrbinary('RETR ' + filename, f.write)

    def upload_file(self, filename, local_filename=None):
        if local_filename is None:
            local_filename = filename

        with open(local_filename, 'rb') as f:
            self.ftp.storbinary('STOR ' + filename, f)

    def create_directory(self, directory_name):
        self.ftp.mkd(directory_name)

    def create_file(self, filename):
        self.ftp.storbinary('STOR ' + filename, io.BytesIO())

    def delete_file_or_directory(self, name):
        try:
            self.ftp.delete(name)  # Попытка удалить как файл
        except:
            self.ftp.rmd(name)  # Если не удалось, попытка удалить как директорию

    def close(self):
        self.ftp.quit()

class MainWindow(tk.Tk):
    def __init__(self, ftp_client):
        super().__init__()

        self.geometry("1280x720")
        self.title("FTP Client")

        self.ftp_client = ftp_client

        # Создание поля ввода для отображения и изменения текущего пути
        self.path_entry = tk.Entry(self)
        self.path_entry.pack(side=tk.LEFT)

        # Создание кнопки для перехода по пути
        self.go_button = ttk.Button(self, text="Перейти", command=self.go_to_directory)
        self.go_button.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH, expand=1)

        # Создание кнопки "Назад"
        self.back_button = ttk.Button(self, text="Назад", command=self.go_back)
        self.back_button.pack(side=tk.LEFT)

        self.download_button = ttk.Button(self, text="Скачать", command=self.download_file)
        self.download_button.pack(side=tk.LEFT)

        # Создание кнопки "Редактировать соединение"
        self.edit_connection_button = ttk.Button(self, text="Редактировать соединение", command=self.edit_connection)
        self.edit_connection_button.pack(side=tk.LEFT)

        self.create_dir_button = ttk.Button(self, text="Создать папку", command=self.create_directory)
        self.create_dir_button.pack(side=tk.LEFT)

        self.create_file_button = ttk.Button(self, text="Создать файл", command=self.create_file)
        self.create_file_button.pack(side=tk.LEFT)

        self.refresh_button = ttk.Button(self, text="Обновить", command=self.populate_tree)
        self.refresh_button.pack(side=tk.LEFT)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Удалить", command=self.delete_file_or_directory)

        self.tree.bind("<Button-3>", self.show_context_menu)

        self.populate_tree()

    def populate_tree(self, directory=''):
        self.tree.delete(*self.tree.get_children())  # Очистка дерева
        self.ftp_client.change_directory(directory)  # Переход в директорию
        files = self.ftp_client.list_files()

        for file in files:
            self.tree.insert('', 'end', text=file, values=(file,))
        
        # Обновление поля ввода текущего пути
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.ftp_client.get_current_directory())

    def go_to_directory(self):
        path = self.path_entry.get()  # Получение пути из поля ввода
        try:
            self.ftp_client.change_directory(path)
            self.populate_tree(path)
        except:
            tkinter.messagebox.showinfo("Not a directory", f"{path} is not a directory")

    def go_back(self):
        self.ftp_client.change_directory('..')  # Переход на уровень вверх
        self.populate_tree()

    def on_close(self):
        self.ftp_client.close()
        self.destroy()

    def edit_connection(self):
        self.ftp_client.close()
        self.destroy()
        login_window = LoginWindow(self.master)

    def download_file(self):
        selected_item = self.tree.selection()[0]  # Получение выбранного элемента
        filename = self.tree.item(selected_item)['text']  # Получение имени файла
        download_dir = tkinter.filedialog.askdirectory()  # Открытие диалога выбора директории
        if download_dir:  # Если пользователь выбрал директорию
            try:
                self.ftp_client.download_file(filename, download_dir)  # Скачивание файла
                tkinter.messagebox.showinfo("Download successful", f"File {filename} downloaded successfully")
            except Exception as e:
                print(f"Failed to download file: {e}")
                tkinter.messagebox.showerror("Download Error", f"Failed to download file: {e}")

    def create_directory(self):
        directory_name = tkinter.simpledialog.askstring("Создать папку", "Введите имя папки:")
        if directory_name:  # Если пользователь ввел имя папки
            try:
                self.ftp_client.create_directory(directory_name)  # Создание папки
                tkinter.messagebox.showinfo("Успех", f"Папка {directory_name} успешно создана")
                self.populate_tree()  # Обновление дерева файлов
            except Exception as e:
                print(f"Failed to create directory: {e}")
                tkinter.messagebox.showerror("Ошибка", f"Не удалось создать папку: {e}")

    def create_file(self):
        filename = tkinter.simpledialog.askstring("Создать файл", "Введите имя файла:")
        if filename:  # Если пользователь ввел имя файла
            try:
                self.ftp_client.create_file(filename)  # Создание файла
                tkinter.messagebox.showinfo("Успех", f"Файл {filename} успешно создан")
                self.populate_tree()  # Обновление дерева файлов
            except Exception as e:
                print(f"Failed to create file: {e}")
                tkinter.messagebox.showerror("Ошибка", f"Не удалось создать файл: {e}")

    def show_context_menu(self, event):
        # Отображение контекстного меню
        self.context_menu.post(event.x_root, event.y_root)

    def delete_file_or_directory(self):
        selected_item = self.tree.selection()[0]  # Получение выбранного элемента
        name = self.tree.item(selected_item)['text']  # Получение имени файла или папки

        try:
            self.ftp_client.delete_file_or_directory(name)  # Удаление файла или папки
            tkinter.messagebox.showinfo("Успех", f"{name} успешно удален")
            self.populate_tree()  # Обновление дерева файлов
        except Exception as e:
            print(f"Failed to delete {name}: {e}")
            tkinter.messagebox.showerror("Ошибка", f"Не удалось удалить {name}: {e}")

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("1280x720")  # Установка размера окна
        self.title("FTP Client - Login")  # Установка заголовка окна

        # Создание меток и полей ввода
        tk.Label(self, text="Host:").grid(row=0, column=0, sticky="e")
        self.host_entry = tk.Entry(self)
        self.host_entry.grid(row=0, column=1)
        self.host_entry.insert(0, "localhost")

        tk.Label(self, text="Username:").grid(row=1, column=0, sticky="e")
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=1, column=1)
        self.username_entry.insert(0, "minen")

        tk.Label(self, text="Password:").grid(row=2, column=0, sticky="e")
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=2, column=1)
        self.password_entry.insert(0, "e4772381")

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
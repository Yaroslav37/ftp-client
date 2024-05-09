import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog
from ftp_client import FTPClient
import os

class MainWindow(tk.Tk):
    def __init__(self, ftp_client):
        super().__init__()

        self.geometry("1280x720")
        self.title("FTP Client")

        self.ftp_client = ftp_client

        # Создание поля ввода для поиска
        self.search_entry = tk.Entry(self)
        self.search_entry.pack(side=tk.TOP, fill=tk.X)

        # Создание кнопки для поиска
        self.search_button = ttk.Button(self, text="Поиск", command=self.search)
        self.search_button.pack(side=tk.TOP, fill=tk.X)

        # Создание дерева
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH, expand=1)

        self.tree.tag_configure('file', foreground='grey')
        self.tree.tag_configure('dir', foreground='orange')

        # Создание поля ввода для отображения и изменения текущего пути
        self.path_entry = tk.Entry(self)
        self.path_entry.pack(side=tk.LEFT)

        # Создание кнопки для перехода по пути
        self.go_button = ttk.Button(self, text="Перейти", command=self.go_to_directory)
        self.go_button.pack(side=tk.LEFT)

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

        self.upload_button = ttk.Button(self, text="Загрузить", command=self.upload_file)
        self.upload_button.pack(side=tk.LEFT)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Удалить", command=self.delete_file_or_directory)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu.add_command(label="Информация", command=self.show_file_info) 

        self.populate_tree()

    def show_file_info(self):
        selected_item = self.tree.selection()[0]  # Получение выбранного элемента
        filename = self.tree.item(selected_item)['text']  # Получение имени файла
        try:
            file_info = self.ftp_client.get_file_info(filename)  # Получение информации о файле
            tkinter.messagebox.showinfo("Информация о файле", file_info)  # Отображение информации о файле в диалоговом окне
        except Exception as e:
            print(f"Failed to get file info: {e}")
            tkinter.messagebox.showerror("Ошибка", f"Не удалось получить информацию о файле: {e}")

    def search(self):
        # Получаем текст из поля ввода
        search_text = self.search_entry.get()

        # Получаем список файлов и директорий
        files_and_dirs = self.ftp_client.list_files_and_dirs()

        # Ищем файлы и директории, которые содержат текст из поля ввода
        matching_files_and_dirs = [f for f in files_and_dirs if search_text in f]

        # Очищаем дерево
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Заполняем дерево найденными файлами и директориями
        for entry in matching_files_and_dirs:
            details, name = entry.split('; ', 1)
            details = details.split(';')
            type_ = next((item.split('=')[1] for item in details if item.startswith('type')), None)
            if type_ == 'file':
                self.tree.insert('', 'end', text=name, values=(name,), tags=('file',))
            elif type_ == 'dir':
                self.tree.insert('', 'end', text=name, values=(name,), tags=('dir',))

    def populate_tree(self, directory=''):
        self.tree.tag_configure('file', foreground='grey')
        self.tree.tag_configure('dir', foreground='orange')
        
        for i in self.tree.get_children():
            self.tree.delete(i)

        files_and_dirs = self.ftp_client.list_files_and_dirs()

        for entry in files_and_dirs:
            details, name = entry.split('; ', 1)
            details = details.split(';')
            type_ = next((item.split('=')[1] for item in details if item.startswith('type')), None)
            if type_ == 'file':
                self.tree.insert('', 'end', text=name, values=(name,), tags=('file',))
            elif type_ == 'dir':
                self.tree.insert('', 'end', text=name, values=(name,), tags=('dir',))


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
        from login_window import LoginWindow
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

    def upload_file(self):
        filename = tkinter.filedialog.askopenfilename()  # Открытие диалога выбора файла
        if filename:  # Если пользователь выбрал файл
            try:
                basename = os.path.basename(filename)  # Получение имени файла без пути
                self.ftp_client.upload_file(basename, filename)  # Загрузка файла
                tkinter.messagebox.showinfo("Upload successful", f"File {basename} uploaded successfully")
            except Exception as e:
                print(f"Failed to upload file: {e}")
                tkinter.messagebox.showerror("Upload Error", f"Failed to upload file: {e}")
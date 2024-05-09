from ftplib import FTP
import os
import io

class FTPClient:
    def __init__(self, host, port, username, password):
        self.ftp = FTP()
        self.ftp.connect(host, int(port))
        self.ftp.login(username, password)

    def change_directory(self, path):
        self.ftp.cwd(path)

    def rename(self, old_name, new_name):
        self.ftp.rename(old_name, new_name)

    def list_files(self):
        return self.ftp.nlst()

    def get_current_directory(self):
        return self.ftp.pwd()

    def download_file(self, filename, download_dir):
        local_filename = os.path.join(download_dir, filename)

        with open(local_filename, 'wb') as f:
            self.ftp.retrbinary('RETR ' + filename, f.write)

    def is_directory(self, name):
        current = self.ftp.pwd()  # сохраняем текущую директорию
        try:
            self.ftp.cwd(name)  # пытаемся перейти в директорию
            self.ftp.cwd(current)  # возвращаемся обратно
            return True
        except Exception as e:
            return False
    
    def download_directory(self, directory, local_directory):
        try:
            if not os.path.exists(local_directory):  # Проверяем, существует ли уже директория
                os.mkdir(local_directory)  # Создаем локальную папку
        except OSError:
            pass

        self.ftp.cwd(directory)  # Переходим в папку на FTP сервере

        items = self.ftp.nlst()  # Получаем список файлов и папок

        for item in items:
            if item == '.DS_Store':  # Пропускаем файлы .DS_Store
                continue
            local_path = os.path.join(local_directory, item)
            if self.is_directory(item):  # Если это папка, скачиваем ее рекурсивно
                self.download_directory(item, local_path)
            else:  # Если это файл, скачиваем его
                self.download_file(item, local_directory)  # Исправлено здесь

        self.ftp.cwd("..")  # Возвращаемся назад


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
            self.ftp.delete(name)
        except:
            self.delete_directory(name)

    def delete_directory(self, directory):
        self.ftp.cwd(directory)

        items = self.ftp.nlst()

        for item in items:
            try:
                self.ftp.delete(item)
            except:
                self.delete_directory(item)

        self.ftp.cwd("..")

        self.ftp.rmd(directory)

    def list_files_and_dirs(self):
        files_and_dirs = []
        self.ftp.retrlines('MLSD', files_and_dirs.append)
        return files_and_dirs

    def close(self):
        self.ftp.quit()

    def get_file_info(self, filename):
        try:
            
            response = []
            self.ftp.retrlines('LIST ' + filename, response.append)
            file_info = response[0] if response else None

            if file_info:
                parts = file_info.split()
                file_type = parts[0][0]  # Тип файла
                name = parts[-1]  # Имя файла

                size = parts[4]  # Размер файла
                modified_date = ' '.join(parts[5:8])  # Дата последней модификации
                file_format = name.split('.')[-1] if '.' in name else ''  # Формат файла
                return f"Имя файла: {name}\nФормат: {file_format}\nРазмер: {size} байт\nДата изменения: {modified_date}"
            else:
                return None
        except Exception as e:
            print(f"Failed to get file info: {e}")
            return None
        
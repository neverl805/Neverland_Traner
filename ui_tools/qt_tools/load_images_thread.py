import os

from PyQt5.QtCore import QThread, pyqtSignal


class Load_Images(QThread):
    response = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.folder_path = None

    def run(self):
        try:
            images_list = [f for f in os.listdir(self.folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'webp', 'bmp'))]
            for i in images_list:
                self.response.emit({'type': 'add', 'item': i})
            self.response.emit({'type': 'finish','image_files_list':images_list})
        except Exception as e:
            self.response.emit({'type': 'errors', 'msg': str(e)})
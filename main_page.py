from PySide6 import QtCore, QtGui
from PySide6.QtUiTools import QUiLoader
from pymongo import MongoClient

import os
from dotenv import load_dotenv

from image_loader import Images

load_dotenv('.env')


loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']



class MainPage(QtCore.QObject):
    def __init__(self, uid):
        super().__init__()
        self.ui = loader.load('./interfaces/main_page.ui', None)
        self.fillingProjectList(uid)

        # TODO: Все-таки лоадер картинок нужно оптимизировать, чтобы он был универсальным для всех файлов
        self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
        self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
        self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
        self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))

    def show(self):
        self.ui.show()

    def fillingProjectList(self, uid):
        res = list(projects.find({'owner': uid}))
        for project in res:
            print(project["title"])
            self.ui.projects_list.addItem(project["title"])
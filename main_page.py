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

        Images.load_image(self, 'main_page')

    def show(self):
        self.ui.show()

    def fillingProjectList(self, uid):
        res = list(projects.find({'owner': uid}))
        for project in res:
            print(project["title"])
            self.ui.projects_list.addItem(project["title"])
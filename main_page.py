from PySide6 import QtCore
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

    def show(self):
        self.ui.show()

    def fillingProjectList(self, uid):
        pj = list(projects.find({'owner': uid}))
        for i in range(len(pj)):
            print(pj[i]["title"])
            self.ui.projects_list.addItem(pj[i]["title"])
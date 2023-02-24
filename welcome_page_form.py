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

def findUid(login):
    user = users.find_one({'login': login})
    return user['uid']

class WelcomePageForm(QtCore.QObject):
    def __init__(self, login):
        super().__init__()
        self.ui = loader.load('./interfaces/welcome_page.ui', None)
        self.ui_create = loader.load('./interfaces/create_new_project_form.ui', None)
        self.ui.create_card.setVisible(False)
        self.ui.sp_new_project.clicked.connect(self.createNewProject)
        self.ui.new_project.clicked.connect(self.createNewProject)
        self.user_login = login

        Images.load_image(self)

        self.ui.welcome_user.setText(f'Приветcтвуем, {self.user_login}!')

    def show(self):
        self.ui.show()

    def createNewProject(self):
        self.ui.sp_new_project.setEnabled(False)
        self.ui.new_project.setEnabled(False)
        self.ui_create.show()
        self.ui_create.back.clicked.connect(self.closeCreateNewProjectPage)
        self.ui_create.create_pj.clicked.connect(self.newProject)

    def closeCreateNewProjectPage(self):
        self.ui.sp_new_project.setEnabled(True)
        self.ui.new_project.setEnabled(True)
        self.ui_create.newproject_name.setText('')
        self.ui_create.close()

    def newProject(self):
        if self.ui_create.newproject_name.text() != '':
            self.ui.create_card.setVisible(True)
            self.ui.welcome_user.setVisible(False)
            self.ui.label_6.setVisible(False)
            self.ui.label_12.setVisible(False)
            self.ui.sp_new_project.setVisible(False)
            self.ui.projects_list.addItem(self.ui_create.newproject_name.text())
            projects.insert_one({
                "title": self.ui_create.newproject_name.text(),
                "owner": findUid(self.user_login),
                "bugs": 0,
                "deadlines": 0,
                "tags": 0,
            })
            print(f'Title: {self.ui_create.newproject_name.text()}, owner: {self.user_login}, bugs: 0, deadlines: 0, tags: 0')
            self.closeCreateNewProjectPage()
        else:
            self.ui_create.newproject_name.setPlaceholderText ("Введите название проекта!")
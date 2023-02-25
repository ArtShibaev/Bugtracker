from PySide6 import QtCore, QtGui
from PySide6.QtUiTools import QUiLoader
from pymongo import MongoClient
from datetime import datetime

import os
from dotenv import load_dotenv

from bug_card import BugCard
from image_loader import Images

load_dotenv('.env')


loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']

def getUserInfo(login):
    user = users.find_one({'login': login})
    return user

class MainPage(QtCore.QObject):
    def __init__(self, uid, login):
        super().__init__()
        self.ui = loader.load('./interfaces/main_page.ui', None)
        self.ui_create = loader.load('./interfaces/create_new_project_form.ui', None)
        self.ui.new_project.clicked.connect(self.createNewProject)
        self.fillingProjectList(uid)
        certainProject = projects.find_one({'owner': uid})
        self.user_login = login
        self.fillBugCards(certainProject)

        Images.load_image(self, 'main_page')

    def show(self):
        self.ui.show()

    def fillingProjectList(self, uid):
        res = list(projects.find({'owner': uid}))
        for project in res:
            self.ui.projects_list.addItem(project["title"])

    def fillBugCards(self, project):
        for bug in project['bugs']:
            bug = BugCard(bug['title'], datetime.utcfromtimestamp(bug['createdDate']/1000).strftime('%d.%m.%Y %H:%M'), bug['author'], bug['assignee'], bug['tags'], bug['criticality'])
            self.ui.bug_cards.addWidget(bug)

    def createNewProject(self):
        self.ui.new_project.setEnabled(False)
        self.ui.create_card.setEnabled(False)
        self.ui_create.show()
        self.ui_create.back.clicked.connect(self.closeCreateNewProjectPage)
        self.ui_create.create_pj.clicked.connect(self.newProject)

    def closeCreateNewProjectPage(self):
        self.ui.new_project.setEnabled(True)
        self.ui.create_card.setEnabled(True)
        self.ui_create.newproject_name.setText('')
        self.ui_create.close()

    def newProject(self):
        if self.ui_create.newproject_name.text() != '':
            self.ui.projects_list.addItem(self.ui_create.newproject_name.text())
            projects.insert_one({
                "title": self.ui_create.newproject_name.text(),
                "owner": getUserInfo(self.user_login)['uid'],
                "bugs": [],
                "deadlines": [],
                "tags": [
                    {"name": "Баг", "color": "#D73A4A"},
                    {"name": "Дубликат", "color": "#CFD3D7"},
                    {"name": "Улучшение", "color": "#A2EEEF"},
                    {"name": "Нужна помощь", "color": "#008672"},
                    {"name": "Не будет исправлено", "color": "#FFFFFF"},
                ],
            })
            print(f'Title: {self.ui_create.newproject_name.text()}, owner: {self.user_login}, bugs: 0, deadlines: 0, tags: 0')
            self.closeCreateNewProjectPage()
        else:
            self.ui_create.newproject_name.setPlaceholderText("Введите название проекта")



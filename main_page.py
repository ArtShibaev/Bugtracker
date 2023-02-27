from PySide6 import QtCore, QtGui
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QPushButton, QComboBox
from pymongo import MongoClient
from datetime import datetime

import os
from dotenv import load_dotenv

from bug_card import BugCard
from image_loader import Images
from config import Config as styles

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
        self.ui_create_project = loader.load('./interfaces/create_new_project_form.ui', None)
        self.ui_create_card = loader.load('./interfaces/new_bug_card.ui', None)

        self.ui.new_project.clicked.connect(self.createNewProject)
        self.ui.create_card.clicked.connect(self.createNewBugCard)

        self.fillingProjectList(uid)
        self.certainProject = projects.find_one({'owner': uid})
        self.loadBugCards(self.certainProject)

        self.ui.projects_list.currentIndexChanged.connect(self.reloadProjectInfo)

        self.user_login = login

        Images.load_image(self, 'main_page')

    def show(self):
        self.ui.show()

    def fillingProjectList(self, uid):
        res = list(projects.find({'owner': uid}))
        for project in res:
            self.ui.projects_list.addItem(project["title"])

    def createNewBugCard(self, project):
        for x in self.ui.findChildren(QPushButton) + self.ui.findChildren(QComboBox):
            x.setEnabled(False)
        self.ui_create_card.show()
        self.ui_create_card.cancel_bug_card.clicked.connect(self.closeCreateNewBugCard)

        for tag in range(len(self.certainProject['tags'])):
            self.ui_create_card.tags.addItem(self.certainProject['tags'][tag]['name'])
        self.ui_create_card.tags.addItem('+ Создать новый')

        self.ui_create_card.criticality.addItem("Низкая")
        self.ui_create_card.criticality.addItem("Средняя")
        self.ui_create_card.criticality.addItem("Высокая")
        self.ui_create_card.assignee.addItem("Нет")
        # еще нужно добавлять в дропдаун всех участников команды
        self.ui_create_card.assignee.addItem(self.user_login)
        # self.ui_create_card.create_bug_card.clicked.connect(self.recordBugData)

        # project['bugs'].append({...})
        # projects.updateOne({...}, project)

    def closeCreateNewBugCard(self):
        for x in self.ui.findChildren(QPushButton) + self.ui.findChildren(QComboBox):
            x.setEnabled(True)
        self.ui_create_card.close()
        self.ui_create_card.title.setText('')
        self.ui_create_card.description.setText('')
        self.ui_create_card.reproduction.setText('')
        self.ui_create_card.tags.clear()
        self.ui_create_card.criticality.clear()
        self.ui_create_card.assignee.clear()


    def loadBugCards(self, project):
        self.clearLayout(self.ui.bug_cards.layout())
        for bug in project['bugs'][:3]:
            bug = BugCard(bug['title'], datetime.utcfromtimestamp(bug['createdDate']/1000).strftime('%d.%m.%Y %H:%M'), bug['author'], bug['assignee'], bug['tags'], bug['criticality'])
            self.ui.bug_cards.addWidget(bug)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def createNewProject(self):
        for x in self.ui.findChildren(QPushButton):
            x.setEnabled(False)
        self.ui_create_project.show()
        self.ui_create_project.back.clicked.connect(self.closeCreateNewProject)
        self.ui_create_project.create_pj.clicked.connect(self.newProject)

    def closeCreateNewProject(self):
        for x in self.ui.findChildren(QPushButton):
            x.setEnabled(True)
        self.ui.new_project.setEnabled(True)
        self.ui.create_card.setEnabled(True)
        self.ui_create_project.newproject_name.setText('')
        self.ui_create_project.close()

    def reloadProjectInfo(self):
        project = projects.find_one({'title': self.ui.projects_list.currentText()})
        self.loadBugCards(project)


    def newProject(self):
        if self.ui_create_project.newproject_name.text() != '':
            self.ui.projects_list.addItem(self.ui_create_project.newproject_name.text())
            projects.insert_one({
                "title": self.ui_create_project.newproject_name.text(),
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
            self.closeCreateNewProjectPage()
        else:
            self.ui_create_project.newproject_name.setPlaceholderText("Введите название проекта")



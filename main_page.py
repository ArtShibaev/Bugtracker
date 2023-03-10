import random
import textwrap
import time
import requests

from PySide6 import QtCore, QtGui
from PySide6.QtCore import *
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from pymongo import MongoClient
import datetime

import os
from dotenv import load_dotenv

from bug_card import BugCard
from bug_page import BugPage
from image_loader import Images
from config import Config

load_dotenv('.env')


loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']
teams = db['teams']

def getFullUserInfo(type, value):
    if type == "login":
        user = users.find_one({"login": value})
    elif type == "uid": user = users.find_one({"uid": value})
    else: user = None
    return user

def getFullUserTeamInfo(type, value):
    if type == "tid":
        team = teams.find_one({"tid": value})
    elif type == "admin": team = teams.find_one({"admin": value})
    else: team = None
    return team

backgrounds = [
    ('background: qlineargradient(spread:repeat, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(108, 87, 193, 255), stop:1 rgba(72, 38, 138, 255));border-radius: 14px;}', 'color:white;background:transparent;font-size:14px;'),
    ('background: qlineargradient(spread:repeat, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(253, 225, 159, 255), stop:1 rgba(218, 189, 88, 255));border-radius: 14px;}', 'color:black;background:transparent;font-size:14px;'),
    ('background: qlineargradient(spread:repeat, x1:0.5, y1:0, x2:0.5, y2:1, stop:0 rgba(169, 235, 216, 255), stop:1 rgba(102, 197, 157, 255));border-radius: 14px;}', 'color:black;background:transparent;font-size:14px;'),
]

project_l = []

class MainPage(QtCore.QObject):
    def __init__(self, uid, login):
        super().__init__()
        self.ui = loader.load('./interfaces/main_page.ui', None)
        self.ui_create_project = loader.load('./interfaces/create_new_project_form.ui', None)
        self.ui_create_card = loader.load('./interfaces/new_bug_card.ui', None)
        self.ui_new_member = loader.load('./interfaces/new_member.ui', None)

        self.user_login = login

        self.reloadProjectInfo()

        self.certainProject = projects.find_one({'owner': uid})
        if self.certainProject == None:
            for team in list(teams.find({})):
                if uid == team['admin']:
                    self.certainProject = projects.find_one({'owner': team['tid']})

        self.ui.new_project.clicked.connect(self.createNewProject)
        self.ui.create_card.clicked.connect(self.createNewBugCard)
        self.ui.new_member.clicked.connect(self.sendJoinRequest)

        self.ui.projects_list.currentIndexChanged.connect(self.reloadProjectInfo)

        Images.load_image(self, 'main_page')

    def show(self):
        self.ui.show()

    def fillingTeamList(self, project):
        self.clearLayout(self.ui.team.layout())

        crown = QPixmap('./images/crown.png')

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        pixmap = QPixmap()

        if project['owner'] == getFullUserInfo('login', self.user_login)['uid']:
            pixmap.loadFromData(requests.get(getFullUserInfo('login', self.user_login)['image']).content)

            member = QPushButton(QtGui.QIcon(pixmap), textwrap.shorten(self.user_login, 18, placeholder='...'))
            crown = QPushButton(QtGui.QIcon(crown), textwrap.shorten('', 10))
            member.setIconSize(QSize(30, 30))
            member.setStyleSheet(Config.membersStyleSheet)
            layout.addWidget(member)
            layout.addWidget(crown)
            main_layout.addLayout(layout)
        else:
            current_team = teams.find_one({'tid': self.certainProject['owner']})
            admin = users.find_one({'uid': current_team['admin']})

            pixmap.loadFromData(requests.get(admin['image']).content)

            member = QPushButton(QtGui.QIcon(pixmap), textwrap.shorten(admin['login'], 18, placeholder='...'))
            crown = QPushButton(QtGui.QIcon(crown), textwrap.shorten('', 10))
            member.setIconSize(QSize(30, 30))
            member.setStyleSheet(Config.membersStyleSheet)
            layout.addWidget(member)
            layout.addWidget(crown)
            main_layout.addLayout(layout)
            for members in current_team['members']:
                user = users.find_one({'uid': members})

                pixmap.loadFromData(requests.get(user['image']).content)

                member = QPushButton(QtGui.QIcon(pixmap), textwrap.shorten(user['login'], 18, placeholder='...'))
                member.setIconSize(QSize(30, 30))
                member.setStyleSheet(Config.membersStyleSheet)
                main_layout.addWidget(member)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.ui.team.setWidget(widget)

    #def showMenu(self):


    def sendJoinRequest(self):
        for x in self.ui.findChildren(QPushButton) + self.ui.findChildren(QComboBox):
            x.setEnabled(False)
        self.ui_new_member.show()
        self.ui_new_member.back.clicked.connect(self.closeSendJoinRequest)
        self.ui_new_member.add.clicked.connect(self.addNewUser)

    def closeSendJoinRequest(self):
        for x in self.ui.findChildren(QPushButton) + self.ui.findChildren(QComboBox):
            x.setEnabled(True)
        self.ui_new_member.close()

    def addNewUser(self):
        user = getFullUserInfo('login', self.ui_new_member.user_login.text())

        if self.ui_new_member.user_login.text() != '':
            if user is not None:
                project = projects.find_one({'title': self.ui.projects_list.currentText()})
                owner = str(project['owner'])
                if owner.startswith('t_'):
                    team = teams.find_one({'tid': owner})
                    if team is not None and team['admin'] == getFullUserInfo('login', self.user_login)['uid']:
                        if user['uid'] not in team['members']:
                            team['members'].append(user['uid'])
                            teams.update_one({'tid': team['tid']}, {'$set': {"members": team['members']}})
                            self.fillingTeamList(self.certainProject)
                            self.closeSendJoinRequrst()
                            self.ui_new_member.user_login.clear()
                            self.ui_new_member.user_login.setPlaceholderText('Логин пользователя')
                        else: print('Участник уже в команде')
                    else: print('Вы не обладаете правами администратора')
                else:
                    if user['uid'] != getFullUserInfo('login', self.user_login)['uid']:
                        teams.insert_one({
                            "tid": 't_' + str(random.randrange(111111, 999999, 5)),
                            "admin": getFullUserInfo('login', self.user_login)['uid'],
                            "members": [],
                        })
                        team = getFullUserTeamInfo('admin', self.certainProject['owner'])
                        team["members"].append(user['uid'])
                        teams.update_one({"tid": team['tid']}, {'$set': {"members": team['members']}})
                        projects.update_one({"title": self.certainProject['title']}, {'$set': {"owner": getFullUserTeamInfo('admin', getFullUserInfo('login', self.user_login)['uid'])['tid']}})
                        self.fillingTeamList(self.certainProject)
                        self.closeSendJoinRequrst()
                        self.ui_new_member.user_login.clear()
                        self.ui_new_member.user_login.setPlaceholderText('Логин пользователя')
                    else: print('Участник уже в команде')
            else: print('Пользователь не найден')
        else: print('Введите логин пользователя')

    def fillingProjectList(self, uid):
        if projects.find_one({'owner': uid}):
            for project in projects.find({'owner': uid}):
                if project["title"] not in project_l:
                    self.ui.projects_list.addItem(project["title"])
                    project_l.append(project["title"])


        for team in list(teams.find({})):
            if uid == team['admin'] or uid in team['members']:
                for project in list(projects.find({'owner': team['tid']})):
                    if project["title"] not in project_l:
                        self.ui.projects_list.addItem(project["title"])
                        project_l.append(project["title"])

    def createNewBugCard(self):
        for x in self.ui.findChildren(QPushButton) + self.ui.findChildren(QComboBox):
            x.setEnabled(False)
        self.ui_create_card.show()
        self.ui_create_card.cancel_bug_card.clicked.connect(self.closeCreateNewBugCard)

        for tag in range(len(self.certainProject['tags'])):
            self.ui_create_card.tags.addItem(self.certainProject['tags'][tag]['name'])
        self.ui_create_card.tags.addItem('+ Создать новый')

        criticalityLevel = ["Низкая", "Средняя", "Высокая"]
        for crit in criticalityLevel:
            self.ui_create_card.criticality.addItem(crit)

        self.ui_create_card.assignee.addItem("Нет")

        self.ui_create_card.assignee.addItem(self.user_login)
        if self.certainProject['owner'].startswith('t_'):
            certainTeam = teams.find_one({'tid': self.certainProject['owner']})
            members = certainTeam['members']

            for user_id in members:
                self.ui_create_card.assignee.addItem(users.find_one({'uid': user_id})['login'])

            if certainTeam['admin'] != getFullUserInfo('login', self.user_login)['uid']:
                self.ui_create_card.assignee.setEnabled(False)

        self.ui_create_card.create_bug_card.clicked.connect(self.recordBugData)

    def recordBugData(self):

        if self.ui_create_card.criticality.currentText() == 'Высокая':
            criticality = 'high'
        elif self.ui_create_card.criticality.currentText() == 'Средняя':
            criticality = 'medium'
        elif self.ui_create_card.criticality.currentText() == 'Низкая':
            criticality = 'low'

        styles = random.choice(backgrounds)

        if self.ui_create_card.assignee.currentText() == 'Нет':
            assignee = 'Нет'
        else:
            assignee = getFullUserInfo('login', self.ui_create_card.assignee.currentText())['uid']

        deadline = int(time.mktime(datetime.datetime.strptime(self.ui_create_card.deadline.date().toString('yyyy-MM-dd'), '%Y-%m-%d').timetuple()))*1000

        # Массив тегов должен заполняться всеми выбранными в дропдауне элементами
        tags = [self.ui_create_card.tags.currentText()]

        project = self.certainProject
        project['bugs'].append({
            "bid": "b_"+str(random.randrange(111111, 999999, 5)),
            "title": self.ui_create_card.title.text(),
            "description": self.ui_create_card.description.toPlainText(),
            "actual_result": self.ui_create_card.actual_result.toPlainText(),
            "supposed_result": self.ui_create_card.supposed_result.toPlainText(),
            "creationDate": round(time.time()*1000),
            "author": getFullUserInfo('login', self.user_login)['uid'],
            "assignee": assignee,
            "deadline": deadline,
            "criticality": criticality,
            "tags": tags,
            "closed": False,
            # Фон и цвет текста карточки
            "styles": styles

        })

        projects.update_one({'title': project['title']}, {'$set': {"bugs": project['bugs']}})

        self.closeCreateNewBugCard()
        self.reloadProjectInfo()


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


    def loadBugs(self, project):
        self.clearLayout(self.ui.bug_cards.layout())
        self.clearLayout(self.ui.scrollArea.layout())

        for bug in project['bugs'][-1:-4:-1]:
            bugCard = BugCard(bug['title'], datetime.datetime.utcfromtimestamp(bug['creationDate']/1000).strftime('%d.%m.%Y %H:%M'), bug['author'], bug['assignee'], bug['tags'], bug['criticality'], bug['styles'])
            self.ui.bug_cards.addWidget(bugCard)
        self.ui.bug_cards.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        widgets = []

        for bug in project['bugs']:
            print(bug['bid'], bug['title'])
            icon = QPixmap('./images/bugInList.png')
            # Исходное изображение черное. Создается маска для всего черного цвета на картинке
            mask = icon.createMaskFromColor(QColor('black'), Qt.MaskOutColor)
            # Маска закрашивается нужным цветом
            icon.fill((QColor('#501AEC' if bug['assignee'] == getFullUserInfo('login', self.user_login)['uid'] else '#7D79A5')))
            icon.setMask(mask)

            bugInList = QPushButton(QtGui.QIcon(icon), textwrap.shorten(bug['title'], 18, placeholder='...'))
            bugInList.setIconSize(QSize(20, 20))
            bugInList.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align: left;}QPushButton:hover{background:#322F6E;border-radius: 10px;}QPushButton:after{content:\'texttext\'}')
            bugInList.clicked.connect(lambda x: self.goToBug(getFullUserInfo('login', self.user_login)['uid'], self.user_login, project, bug['bid']))
            layout.addWidget(bugInList)


        widget = QWidget()
        widget.setLayout(layout)
        self.ui.scrollArea.setWidget(widget)

    def goToBug(self, uid, login, project, bid):
        self.ui.hide()
        self.ui = BugPage(uid, login, project, bid)
        self.ui.show()

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
        self.fillingProjectList(getFullUserInfo('login', self.user_login)['uid'])
        project = projects.find_one({'title': self.ui.projects_list.currentText()})
        self.certainProject = project
        self.loadBugs(project)
        self.fillingTeamList(self.certainProject)

    def newProject(self):
        if self.ui_create_project.newproject_name.text() != '':
            self.ui.projects_list.addItem(self.ui_create_project.newproject_name.text())
            projects.insert_one({
                "title": self.ui_create_project.newproject_name.text(),
                "owner": getFullUserInfo('login', self.user_login)['uid'],
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
            self.closeCreateNewProject()
        else:
            self.ui_create_project.newproject_name.setPlaceholderText("Введите название проекта")


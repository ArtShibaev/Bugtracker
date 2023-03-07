import datetime
import os
import textwrap

from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget
from pymongo import MongoClient

from bug_card import BugCard
from image_loader import Images

loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']
teams = db['teams']

def getUserInfo(login):
    user = users.find_one({'login': login})
    return user

class BugPage(QtCore.QObject):
    def __init__(self, uid, login, project, bid):
        print('Переход на', bid)
        self.uid = uid
        self.login = login
        self.bid = bid
        super().__init__()
        self.ui = loader.load('./interfaces/bug_page.ui', None)
        self.ui.verticalLayout_5.setAlignment(Qt.AlignLeft)

        Images.load_image(self, 'bug_page')
        self.ui.home.clicked.connect(self.goToMainPage)

        self.fillProjectsList(uid)
        # В дропдауне отмечаем тот проект, со страницы которого был переход
        project_index = self.ui.projects_list.findText(project['title'], QtCore.Qt.MatchFixedString)
        if project_index >= 0:
            self.ui.projects_list.setCurrentIndex(project_index)

        self.loadBugs(project)

        self.loadBugInfo(project['bugs'], bid)

    def loadBugInfo(self, bugs, bid):
        for x in bugs:
            if x['bid'] == bid:
                self.bug = x
                print(self.bug)
                break

        self.ui.title.setText(self.bug['title'])

    def show(self):
        self.ui.show()

    def goToMainPage(self):
        from main_page import MainPage

        self.ui.hide()
        self.ui = MainPage(self.uid, self.login)
        self.ui.show()

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())


    def fillProjectsList(self, uid):

        if projects.find_one({'owner': uid}):
            for project in projects.find({'owner': uid}):
                self.ui.projects_list.addItem(project["title"])


        for team in list(teams.find({})):
            if uid == team['admin'] or uid in team['members']:
                for project in list(projects.find({'owner': team['tid']})):
                    self.ui.projects_list.addItem(project["title"])

    def loadBugs(self, project):
        self.clearLayout(self.ui.scrollArea.layout())

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        for bug in project['bugs']:
            print(bug['bid'], bug['title'])
            icon = QPixmap('./images/bugInList.png')
            # Исходное изображение черное. Создается маска для всего черного цвета на картинке
            mask = icon.createMaskFromColor(QColor('black'), Qt.MaskOutColor)
            # Маска закрашивается нужным цветом
            icon.fill((QColor('#501AEC' if bug['assignee'] == getUserInfo(self.login)['uid'] else '#7D79A5')))
            icon.setMask(mask)

            bugInList = QPushButton(QtGui.QIcon(icon), textwrap.shorten(bug['title'], 18, placeholder='...'))
            bugInList.setIconSize(QSize(20, 20))
            if bug['bid'] != self.bid:
                bugInList.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align: left;}QPushButton:hover{background:#322F6E;border-radius: 10px;}')
            else:
                bugInList.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align:left;border-radius: 10px;background:#322F6E}')

            bugInList.clicked.connect(self.loadBugInfo(project['bugs'], bug['bid']))
            layout.addWidget(bugInList)

        widget = QWidget()
        widget.setLayout(layout)
        self.ui.scrollArea.setWidget(widget)

import datetime
import os
import random
import textwrap
import time

from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QComboBox, QLabel
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

def getUserInfo(type, value):
    if type == 'login':
        user = users.find_one({'login': value})
    if type == 'uid':
        user = users.find_one({'uid': value})
    return user

def getUserTeam(uid):
    team = teams.find_one({'admin': uid})
    return team

class BugPage(QtCore.QObject):
    def __init__(self, uid, login, project, bid):
        self.bug = None
        self.uid = uid
        self.login = login
        self.bid = bid
        super().__init__()
        self.ui = loader.load('./interfaces/bug_page.ui', None)
        self.ui_create_project = loader.load('./interfaces/create_new_project_form.ui', None)
        self.ui_create_card = loader.load('./interfaces/new_bug_card.ui', None)

        self.ui.verticalLayout_5.setAlignment(Qt.AlignLeft)

        Images.load_image(self, 'bug_page')
        self.ui.home.clicked.connect(self.goToMainPage)

        self.fillProjectsList(uid)
        # В дропдауне отмечаем тот проект, со страницы которого был переход
        project_index = self.ui.projects_list.findText(project['title'], QtCore.Qt.MatchFixedString)
        if project_index >= 0:
            self.ui.projects_list.setCurrentIndex(project_index)

        from main_page import MainPage
        self.ui.new_project.clicked.connect(self.createNewProject)
        self.ui.create_card.clicked.connect(self.createNewBugCard)

        self.loadBugInfo(project['bugs'], bid)
        self.loadBugs(project)

        # Здесь нужна лямбда-функция, чтобы предотвратить выполнение closeBug, когда компилятор прогоняет весь код при первом рендеринге
        self.ui.close_bug.clicked.connect(lambda x: self.closeBug(project))
        self.ui.assign.clicked.connect(lambda x: self.selfAssign(project))
        self.ui.deny.clicked.connect(lambda x: self.denyBug(project))

        self.loadMessageHistory()
        self.ui.send.clicked.connect(lambda x: self.sendMessage(project))

    def loadBugInfo(self, bugs, bid):
        for x in bugs:
            if x['bid'] == bid:
                self.bug = x
                break

        self.ui.setWindowTitle(f"Багтрекер - {self.bug['title']}")

        self.ui.title.setText(self.bug['title'])
        self.ui.description.setText(self.bug['description'])
        self.ui.actual_result.setText(self.bug['actual_result'])
        self.ui.supposed_result.setText(self.bug['supposed_result'])
        self.ui.reproduction.setText(self.bug['steps'])
        self.ui.tags.setText(', '.join([x for x in self.bug['tags']]))
        self.ui.creationDate.setText(datetime.datetime.utcfromtimestamp(self.bug['creationDate']/1000).strftime('%d.%m.%Y %H:%M'))
        self.ui.author.setText(getUserInfo('uid', self.bug['author'])['login'])
        self.ui.assignee.setText(getUserInfo('uid', self.bug['assignee'])['login'] if str(self.bug['assignee']).isdigit() else 'Нет')
        self.ui.deadline.setText(datetime.datetime.utcfromtimestamp(self.bug['deadline']/1000).strftime('%d.%m.%Y') if str(self.bug['deadline']).isdigit() else 'Нет')

        if self.bug['closed']:
            # TODO: Добавить в бд ключ closedDate
            self.ui.closed.setText(datetime.datetime.utcfromtimestamp(self.bug['closedDate']/1000).strftime('%d.%m.%Y %H:%M'))
            # Зачеркивание текста
            self.ui.title.setStyleSheet('color:white;font-weight:bold;font-size:20px;text-decoration:line-through;')
        else:
            # TODO: Сделать скрытие всей строки "Завершен"
            self.ui.closed.setText('')

        self.ui.creationDate.setAlignment(Qt.AlignRight)
        self.ui.author.setAlignment(Qt.AlignRight)
        self.ui.assignee.setAlignment(Qt.AlignRight)
        self.ui.deadline.setAlignment(Qt.AlignRight)
        self.ui.closed.setAlignment(Qt.AlignRight)

        if self.bug['closed']:
            self.ui.close_bug.setVisible(False)
            self.ui.deny.setVisible(False)
            self.ui.assign.setVisible(False)

        # Да, этот понос из взаимоисключающих условий нужен. Можешь убрать и чекнуть))
        else:
            if self.bug['assignee'] != self.uid:
                self.ui.close_bug.setVisible(False)
            else:
                self.ui.close_bug.setVisible(True)
            if self.bug['assignee'] != self.uid:
                self.ui.deny.setVisible(False)
            else:
                self.ui.deny.setVisible(True)
            if self.bug['assignee'] != 'Нет':
                self.ui.assign.setVisible(False)
            else:
                self.ui.assign.setVisible(True)

    def closeBug(self, project):
        for bug in project['bugs']:
            if bug['bid'] == self.bid:
                bug['closed'] = True
                # 10800 - 3 часа в секундах, чтобы от UTC перейти к московскому времени
                bug['closedDate'] = round(time.time()*1000)+10800
                bug['messages'].append({
                    "author": self.uid,
                    "date": round((time.time()+10800)*1000),
                    "text": "<i>Закрыл баг</i>"
                })
        projects.update_one({'title': project['title']}, {'$set': {'bugs': project['bugs']}})
        self.loadBugInfo(project['bugs'], self.bid)
        self.loadMessageHistory()

    def selfAssign(self, project):
        for bug in project['bugs']:
            if bug['bid'] == self.bid:
                bug['assignee'] = self.uid
                bug['messages'].append({
                    "author": self.uid,
                    "date": round((time.time()+10800)*1000),
                    "text": "<i>Закрепил баг за собой</i>"
                })
        projects.update_one({'title': project['title']}, {'$set': {'bugs': project['bugs']}})
        self.loadBugInfo(project['bugs'], self.bid)
        self.loadBugs(project)
        self.loadMessageHistory()



    def denyBug(self, project):
        for bug in project['bugs']:
            if bug['bid'] == self.bid:
                bug['assignee'] = 'Нет'
                bug['messages'].append({
                    "author": self.uid,
                    "date": round((time.time()+10800)*1000),
                    "text": "<i>Отказался от бага</i>"
                })
        projects.update_one({'title': project['title']}, {'$set': {'bugs': project['bugs']}})
        self.loadBugInfo(project['bugs'], self.bid)
        self.loadBugs(project)
        self.loadMessageHistory()


    def loadMessageHistory(self):
        self.clearLayout(self.ui.messages.layout())

        bug = self.bug
        if bug['messages']:
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop)
            for message in bug['messages']:
                author = f"<b>{getUserInfo('uid', message['author'])['login']}</b>" if message['author'] == self.uid else f"{getUserInfo('uid', message['author'])['login']}"
                item = QLabel(f"{datetime.datetime.utcfromtimestamp(message['date']/1000).strftime('%d.%m.%Y %H:%M')} {author}: {' '.join(message['text'].split())}")
                item.setStyleSheet('color: #fff;')
                layout.addWidget(item)

            widget = QWidget()
            widget.setLayout(layout)
            self.ui.messages.setWidget(widget)

    def sendMessage(self, project):
        bugs = project['bugs']
        for bug in bugs:
            if bug['bid'] == self.bid:
                bug['messages'].append({
                    "author": self.uid,
                    "date": round((time.time()+10800)*1000),
                    "text": self.ui.message.toPlainText()
                })

        projects.update_one({"title": project['title']}, {'$set': {'bugs': bugs}})
        self.ui.message.setPlainText('')
        self.loadMessageHistory()



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
            icon = QPixmap('./images/bugInList.png')
            # Исходное изображение черное. Создается маска для всего черного цвета на картинке
            mask = icon.createMaskFromColor(QColor('black'), Qt.MaskOutColor)
            # Маска закрашивается нужным цветом
            icon.fill((QColor('#501AEC' if bug['assignee'] == getUserInfo('login', self.login)['uid'] else '#7D79A5')))
            icon.setMask(mask)

            bugInList = QPushButton(QtGui.QIcon(icon), textwrap.shorten(bug['title'], 18, placeholder='...'))
            bugInList.setIconSize(QSize(20, 20))
            if bug['bid'] != self.bid:
                bugInList.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align: left;}QPushButton:hover{background:#322F6E;border-radius: 10px;}')
            else:
                bugInList.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align:left;border-radius: 10px;background:#322F6E}')
            bugInList.setProperty('bid', bug['bid'])
            # FIXME: Пофиксить функцию ниже
            bugInList.clicked.connect(self.loadBugInfo(project['bugs'], bugInList.property('bid')))
            layout.addWidget(bugInList)

        widget = QWidget()
        widget.setLayout(layout)
        self.ui.scrollArea.setWidget(widget)

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

            if certainTeam['admin'] != getUserInfo(self.user_login)['uid']:
                self.ui_create_card.assignee.setEnabled(False)

        else:
            certainTeam = getUserTeam(self.certainProject['owner'])


        self.ui_create_card.create_bug_card.clicked.connect(self.recordBugData)

    def recordBugData(self):

        if self.ui_create_card.criticality.currentText() == 'Высокая':
            criticality = 'high'
        elif self.ui_create_card.criticality.currentText() == 'Средняя':
            criticality = 'medium'
        elif self.ui_create_card.criticality.currentText() == 'Низкая':
            criticality = 'low'
        from main_page import backgrounds
        styles = random.choice(backgrounds)

        if self.ui_create_card.assignee.currentText() == 'Нет':
            assignee = 'Нет'
        else:
            assignee = getUserInfo(self.ui_create_card.assignee.currentText())['uid']

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
            "author": getUserInfo(self.user_login)['uid'],
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

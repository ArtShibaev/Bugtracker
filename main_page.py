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
from itertools import groupby
import datetime
import pastebinpy as pbp

import os
from dotenv import load_dotenv

import mailer
from bug_card import BugCard
from bug_page import BugPage
from image_loader import Images
from config import Config
import notifier

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
member_data = []

class MainPage(QtCore.QObject):
    def __init__(self, uid, login, **args):
        super().__init__()
        self.count = 0
        self.ui = loader.load('./interfaces/main_page.ui', None)
        self.ui_create_project = loader.load('./interfaces/create_new_project_form.ui', None)
        self.ui_create_card = loader.load('./interfaces/new_bug_card.ui', None)

        self.ui.new_project.clicked.connect(self.createNewProject)
        self.ui.create_card.clicked.connect(self.createNewBugCard)
        self.ui.settings.clicked.connect(self.goToSettingsPage)
        self.ui_new_member = loader.load('./interfaces/new_member.ui', None)
        self.ui_change_team = loader.load('./interfaces/change_team.ui', None)

        self.user_login = login
        self.uid = uid

        self.fillingProjectList(getFullUserInfo('login', self.user_login)['uid'])

        # Получаю значения оцпионального аргумента - проекта, с которого был переход на главную
        referrer_project = args.get('referrer_project')
        if referrer_project:
            project_index = self.ui.projects_list.findText(args.get('referrer_project')['title'], QtCore.Qt.MatchFixedString)
            self.ui.projects_list.setCurrentIndex(project_index)
            self.certainProject = referrer_project
        else:
            self.certainProject = projects.find_one({'owner': uid})

            if self.certainProject is None:
                for team in list(teams.find({})):
                    if uid == team['admin'] or uid in team['members']:
                        self.certainProject = projects.find_one({'owner': team['tid']})
            self.ui.projects_list.setCurrentIndex(self.ui.projects_list.count()-1)

        self.changeProject()

        self.ui.new_project.clicked.connect(self.createNewProject)
        self.ui.create_card.clicked.connect(self.createNewBugCard)
        self.ui.new_member.clicked.connect(self.sendJoinRequest)
        self.ui.change.clicked.connect(self.showMenu)

        self.ui.projects_list.currentIndexChanged.connect(self.changeProject)


        Images.load_image(self, 'main_page')

    def show(self):
        self.ui.show()

    def changeProject(self):
        self.certainProject = projects.find_one({'title': self.ui.projects_list.currentText()})
        if str(self.certainProject['owner']).startswith('t_'):
            if getFullUserTeamInfo('tid', self.certainProject['owner'])['admin'] != getFullUserInfo('login', self.user_login)['uid']:
                self.ui.new_member.hide()
                self.ui.change.hide()
            else:
                self.ui.new_member.show()
                self.ui.change.show()
        else:
            self.ui.new_member.show()
            self.ui.change.show()
        self.reloadProjectInfo()

    def fillingTeamList(self):
        self.clearLayout(self.ui.team.layout())
        member_data.clear()

        crown_ic = QPixmap('./images/crown.png')

        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(getFullUserInfo('login', self.user_login)['image']).content)
        self.ui.users_photo.setIcon(QtGui.QIcon(pixmap))
        self.ui.users_photo.setIconSize(QSize(40, 40))

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        pixmap = QPixmap()

        if self.certainProject['owner'] == getFullUserInfo('login', self.user_login)['uid']:
            pixmap.loadFromData(requests.get(getFullUserInfo('login', self.user_login)['image']).content)
            member_data.append(self.user_login)

            member = QPushButton(QtGui.QIcon(pixmap), textwrap.shorten(self.user_login, 18, placeholder='...'))
            crown = QPushButton(QtGui.QIcon(crown_ic), textwrap.shorten('', 10))
            member.setIconSize(QSize(30, 30))
            member.setStyleSheet(Config.membersStyleSheet)
            member.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            layout.addWidget(member)
            layout.addWidget(crown)
            main_layout.addLayout(layout)
        else:
            current_team = teams.find_one({'tid': self.certainProject['owner']})
            admin = users.find_one({'uid': current_team['admin']})

            pixmap.loadFromData(requests.get(admin['image']).content)

            member = QPushButton(QtGui.QIcon(pixmap), textwrap.shorten(admin['login'], 18, placeholder='...'))
            member_data.append(admin['login'])
            crown = QPushButton(QtGui.QIcon(crown_ic), textwrap.shorten('', 10))
            member.setIconSize(QSize(30, 30))
            member.setStyleSheet(Config.membersStyleSheet)
            member.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
            layout.addWidget(member)
            layout.addWidget(crown)
            main_layout.addLayout(layout)
            for members in current_team['members']:
                user = users.find_one({'uid': members})

                pixmap.loadFromData(requests.get(user['image']).content)

                member = QPushButton(QtGui.QIcon(pixmap), textwrap.shorten(user['login'], 18, placeholder='...'))
                member_data.append(user['login'])
                member.setIconSize(QSize(30, 30))
                member.setStyleSheet(Config.membersStyleSheet)
                member.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
                main_layout.addWidget(member)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.ui.team.setWidget(widget)

    def showMenu(self):
        self.ui_change_team.show()
        self.ui_change_team.new_admin.clicked.connect(self.newAdmin)
        self.ui_change_team.exclude.clicked.connect(self.deleteUserFromTeam)

    def newAdmin(self):
        if self.ui_change_team.user_login.text() in member_data:
            current_admin = getFullUserInfo('login', self.user_login)['uid']
            new_admin = getFullUserInfo('login', self.ui_change_team.user_login.text())['uid']
            if current_admin == new_admin:
                self.ui_change_team.user_login.clear()
                self.ui_change_team.user_login.setPlaceholderText('Данный пользователь уже администратор')
            else:
                team = getFullUserTeamInfo('tid', self.certainProject['owner'])
                teams.update_one({"tid": team['tid']}, {'$set': {"admin": new_admin}})
                team['members'][team['members'].index(new_admin)] = current_admin
                teams.update_one({"tid": team['tid']}, {'$set': {"members": team['members']}})
                self.ui_change_team.close()
                self.changeProject()
        else:
            self.ui_change_team.user_login.clear()
            self.ui_change_team.user_login.setPlaceholderText('Пользователь не найден')

    def deleteUserFromTeam(self):
        if self.ui_change_team.user_login.text() in member_data:
            duser = getFullUserInfo('login', self.ui_change_team.user_login.text())['uid']
            if getFullUserInfo('login', self.user_login)['uid'] == duser:
                self.ui_change_team.user_login.clear()
                self.ui_change_team.user_login.setPlaceholderText('Администратор не может покинуть команду')
            else:
                team = getFullUserTeamInfo('tid', self.certainProject['owner'])
                team['members'].pop(team['members'].index(duser))
                teams.update_one({"tid": team['tid']}, {'$set': {'members': team['members']}})
                for i in range(len(self.certainProject['bugs'])):
                    if self.certainProject['bugs'][i]['assignee'] == duser:
                        self.certainProject['bugs'][i]['assignee'] = 'Нет'
                projects.update_one({"title": self.certainProject['title']}, {'$set': {'bugs': self.certainProject['bugs']}})
                if len(team['members']) == 0:
                    projects.update_one({"title": self.certainProject['title']}, {'$set': {'owner': getFullUserInfo('login', self.user_login)['uid']}})
                    teams.delete_one({"tid": team['tid']})
                self.ui_change_team.close()
                self.changeProject()
        else:
            self.ui_change_team.user_login.clear()
            self.ui_change_team.user_login.setPlaceholderText('Пользователь не найден')

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
                            self.changeProject()
                            self.closeSendJoinRequest()
                            self.ui_new_member.user_login.clear()
                            self.ui_new_member.user_login.setPlaceholderText('Логин пользователя')
                        else: notifier.sendError('Ошибка добавления пользователя', 'Участник уже в команде')

                    else: notifier.sendError(message='Вы не обладаете правами администратора')
                else:
                    if user['uid'] != getFullUserInfo('login', self.user_login)['uid']:
                        teamID = 't_' + str(random.randrange(111111, 999999, 5))
                        teams.insert_one({
                            "tid": teamID,
                            "admin": getFullUserInfo('login', self.user_login)['uid'],
                            "members": [],
                        })
                        team = getFullUserTeamInfo('tid', teamID)
                        team["members"].append(user['uid'])
                        teams.update_one({"tid": team['tid']}, {'$set': {"members": team['members']}})
                        projects.update_one({"title": self.certainProject['title']}, {'$set': {"owner": teamID}})
                        self.changeProject()
                        self.closeSendJoinRequest()
                        self.ui_new_member.user_login.clear()
                        self.ui_new_member.user_login.setPlaceholderText('Логин пользователя')
                    else: notifier.sendError('Ошибка добавления пользователя', 'Участник уже в команде')
            else: notifier.sendError('Ошибка добавления пользователя', 'Пользователь не найден')
        else: notifier.sendError(message='Введите логин пользователя')

    def fillingDeadlineFrames(self):
        self.ui.bug_list_1.clear()
        self.ui.deadline1.setText('Нет информации')
        self.ui.complete1.setText('Нет информации')
        self.ui.developers1.setText('Нет информации')

        self.ui.bug_list_2.clear()
        self.ui.deadline2.setText('Нет информации')
        self.ui.complete2.setText('Нет информации')
        self.ui.developers2.setText('Нет информации')

        deadlines = []
        statistic_all, statistic_close = 0, 0
        for bug in self.certainProject['bugs']:
            if not bug['closed']:
                deadlines.append(bug['deadline'])
        с_deadlines = list(set(deadlines))
        if len(с_deadlines) == 0:
            self.ui.deadline_frame1.hide()
            self.ui.deadline_frame2.hide()
        else:
            с_deadlines.sort()
            min_deadline = с_deadlines[0]
            self.ui.deadline_frame1.show()
            developers = []
            statistic = 0
            for min_dl_bug in self.certainProject['bugs']:
                if min_dl_bug['deadline'] == min_deadline:
                    statistic_all += min_dl_bug['complexity']
                    self.ui.bug_list_1.addItem(min_dl_bug['title'])
                    self.ui.deadline1.setText(str(min_deadline))
                    if min_dl_bug['closed']: statistic += 1; statistic_close += min_dl_bug['complexity']
                    if min_dl_bug['assignee'] != 'Нет':
                        developers.append(getFullUserInfo('uid', min_dl_bug['assignee'])['login'])
            с_developers = list(set(developers))
            final_list = [el for el, _ in groupby(с_developers)]
            self.ui.complete1.setText(f'{statistic}/{self.ui.bug_list_1.count()}')
            self.ui.developers1.setText(', '.join(map(str, final_list)))
            self.ui.progress1.setMaximum(statistic_all)
            self.ui.progress1.setValue(statistic_close)

        deadlines = []
        statistic_all, statistic_close = 0, 0
        for bug in self.certainProject['bugs']:
            if not bug['closed']:
                deadlines.append(bug['deadline'])
        с_deadlines = list(set(deadlines))
        if len(с_deadlines) == 1: self.ui.deadline_frame2.hide()
        elif len(с_deadlines) > 1:
            с_deadlines.sort()
            min_deadline = с_deadlines[1]
            self.ui.deadline_frame2.show()
            developers = []
            statistic = 0
            for min_dl_bug in self.certainProject['bugs']:
                if min_dl_bug['deadline'] == min_deadline:
                    statistic_all += min_dl_bug['complexity']
                    self.ui.bug_list_2.addItem(min_dl_bug['title'])
                    self.ui.deadline2.setText(str(min_deadline))
                    if min_dl_bug['closed']: statistic += 1; statistic_close += min_dl_bug['complexity']
                    if min_dl_bug['assignee'] != 'Нет':
                        developers.append(getFullUserInfo('uid', min_dl_bug['assignee'])['login'])
            с_developers = list(set(developers))
            final_list = [el for el, _ in groupby(с_developers)]
            self.ui.complete2.setText(f'{statistic}/{self.ui.bug_list_2.count()}')
            self.ui.developers2.setText(', '.join(map(str, final_list)))
            self.ui.progress2.setMaximum(statistic_all)
            self.ui.progress2.setValue(statistic_close)


    def fillingProjectList(self, uid):
        if projects.find_one({'owner': uid}):
            for project in projects.find({'owner': uid}):
                if project["title"] not in project_l:
                    self.ui.projects_list.addItem(project["title"])
                    project_l.append(project["title"])

        # Это возможно вызовет баг :/
        project_l.clear()

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

        self.ui_create_card.assignee.clear()
        self.ui_create_card.tags.clear()
        self.ui_create_card.criticality.clear()

        self.ui_create_card.cancel_bug_card.clicked.connect(self.closeCreateNewBugCard)

        for tag in range(len(self.certainProject['tags'])):
            self.ui_create_card.tags.addItem(self.certainProject['tags'][tag]['name'])
        self.ui_create_card.tags.addItem('+ Создать новый')

        criticalityLevel = ["Низкая", "Средняя", "Высокая"]
        for crit in criticalityLevel:
            self.ui_create_card.criticality.addItem(crit)

        self.ui_create_card.assignee.addItem("Нет")

        self.ui_create_card.assignee.addItem(self.user_login)
        if str(self.certainProject['owner']).startswith('t_'):
            certainTeam = teams.find_one({'tid': self.certainProject['owner']})
            members = certainTeam['members']

            for user_id in members:
                self.ui_create_card.assignee.addItem(getFullUserInfo('uid', user_id)['login'])

            if certainTeam['admin'] != getFullUserInfo('login', self.user_login)['uid']:
                self.ui_create_card.assignee.setEnabled(False)

        self.ui_create_card.horizontalSlider.valueChanged.connect(self.valuechangeHr)
        self.ui_create_card.spinBox.valueChanged.connect(self.valuechangeSp)

        self.ui_create_card.create_bug_card.clicked.connect(self.recordBugData)

    def valuechangeHr(self):
        self.ui_create_card.spinBox.setValue(self.ui_create_card.horizontalSlider.value())

    def valuechangeSp(self):
        self.ui_create_card.horizontalSlider.setValue(self.ui_create_card.spinBox.value())

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


        deadline = datetime.datetime.strptime(self.ui_create_card.deadline.date().toString('yyyy.MM.dd'), '%Y.%m.%d').strftime("%d.%m.%Y")

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
            "styles": styles,
            "messages": [],
            "steps": self.ui_create_card.reproduction.toPlainText(),
            "complexity": self.ui_create_card.horizontalSlider.value(),
            "pastebin_link": pbp.paste(os.environ.get('PASTEBIN_KEY'), self.ui_create_card.code_fragment.toPlainText(), self.ui_create_card.title.text(), privacy="1") if self.ui_create_card.code_fragment.toPlainText() else ""
        })

        if str(project['owner']).startswith('t_'):
            team = teams.find_one({"tid": project['owner']})
            admin = getFullUserInfo('uid', team['admin'])

            # Скопировал словарь созданного сейчас бага
            created_bug = project['bugs'][-1].copy()
            # Удалил ненужные поля
            del created_bug['closed'], created_bug['styles']
            # Заджоинил все ключи и их значения через <br> - это HTML тег, который переносит на новую строку
            content = '<br>'.join([f"<b>{x}</b>: {created_bug[x]}" for x in created_bug])
            subject = f'{project["title"]}: новый баг - {self.ui_create_card.title.text()}'

            if admin['notifications']['new_bugs']:
                mailer.sendMail(admin['email'],
                                subject,
                                f'{content}')

            for x in team['members']:
                user = getFullUserInfo('uid', x)
                if user['notifications']['new_bugs']:
                    mailer.sendMail(user['email'],
                                    subject,
                                    f'{content}')

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


    def loadBugs(self):
        self.clearLayout(self.ui.bug_cards.layout())
        self.clearLayout(self.ui.scrollArea.layout())

        completionList = {}
        for x in self.certainProject['bugs']:
            completionList[x['title']] = x['bid']

        completer = QCompleter([x['title'] for x in self.certainProject['bugs']])
        completer.activated.connect(lambda x: self.goToBug(completionList[x]))

        self.ui.search.setCompleter(completer)

        # Чтобы в карточках не вылезали закрытые баги, я фильтрую
        opened_bugs = list(filter(lambda x: not x['closed'], self.certainProject['bugs']))

        for bug in opened_bugs[-1:-4:-1]:
            bugCard = BugCard(bug['title'], datetime.datetime.utcfromtimestamp(bug['creationDate']/1000).strftime('%d.%m.%Y %H:%M'), bug['author'], bug['assignee'], bug['tags'], bug['criticality'], bug['styles'])
            self.ui.bug_cards.addWidget(bugCard)
        self.ui.bug_cards.setAlignment(Qt.AlignLeft)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        for bug in self.certainProject['bugs']:
            if not bug['closed']:
                icon = QPixmap('./images/bugInList.png')
                # Исходное изображение черное. Создается маска для всего черного цвета на картинке
                mask = icon.createMaskFromColor(QColor('black'), Qt.MaskOutColor)
                # Маска закрашивается нужным цветом
                icon.fill((QColor('#501AEC' if bug['assignee'] == getFullUserInfo('login', self.user_login)['uid'] else '#7D79A5')))
                icon.setMask(mask)

                bugInList = QPushButton(QtGui.QIcon(icon), textwrap.shorten(bug['title'], 18, placeholder='...'))
                bugInList.setIconSize(QSize(20, 20))
                bugInList.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align: left;}QPushButton:hover{background:#322F6E;border-radius: 10px;}QPushButton:after{content:\'texttext\'}')
                bugInList.setProperty('bid', bug['bid'])
                bugInList.clicked.connect(self.partial)
                layout.addWidget(bugInList)


        widget = QWidget()
        widget.setLayout(layout)
        self.ui.scrollArea.setWidget(widget)

    def partial(self):
        sender = self.sender()
        self.goToBug(sender.property('bid'))

    def goToBug(self, bid):
        uid = getFullUserInfo('login', self.user_login)['uid']
        login = self.user_login
        project = self.certainProject
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
        self.loadBugs()
        self.fillingTeamList()
        self.fillingDeadlineFrames()
        self.reloadStatistic()

    def reloadStatistic(self):
        statistic_c, statistic_o = 0, 0
        for bug in self.certainProject['bugs']:
            if bug['closed']:
                statistic_c += 1
            else:
                statistic_o += 1

        self.ui.all_p.setText(str(statistic_c + statistic_o))
        self.ui.open_p.setText(str(statistic_o))
        self.ui.close_p.setText(str(statistic_c))
        if statistic_c + statistic_o > 0:
            self.ui.progress3.setMaximum(statistic_c + statistic_o)
            self.ui.progress3.setValue(statistic_c)
        else:
            self.ui.progress3.setMaximum(1)
            self.ui.progress3.setValue(0)

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
            self.reloadProjectInfo()
        else:
            self.ui_create_project.newproject_name.setPlaceholderText("Введите название проекта")


    def goToSettingsPage(self):
        from settings_page import SettingPage
        self.ui.hide()
        self.ui = SettingPage(self.uid, self.user_login)
        self.ui.show()

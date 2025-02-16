import datetime
import os
import pprint
import random
import textwrap
import time
import webbrowser

import pytz
import requests

from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QColor, QCursor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QComboBox, QLabel, QCompleter
from pymongo import MongoClient
import pastebinpy as pbp


import config
import mailer
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
        self.project = project
        self.bug = list(filter(lambda x: x['bid'] == bid, project['bugs']))[0]
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
        self.ui.settings.clicked.connect(self.goToSettingsPage)

        self.fillProjectsList(uid)
        # В дропдауне отмечаем тот проект, со страницы которого был переход
        project_index = self.ui.projects_list.findText(project['title'], QtCore.Qt.MatchFixedString)
        if project_index >= 0:
            self.ui.projects_list.setCurrentIndex(project_index)

        self.ui.projects_list.currentIndexChanged.connect(self.reloadProjectInfo)

        self.ui.new_project.clicked.connect(self.createNewProject)
        self.ui.create_card.clicked.connect(self.createNewBugCard)

        self.loadBugInfo(project['bugs'], self.bid)
        self.loadBugs(project)

        completionList = {}
        for x in self.project['bugs']:
            completionList[x['title']] = x['bid']

        completer = QCompleter([x['title'] for x in self.project['bugs']])
        completer.activated.connect(lambda x: self.loadBugInfo(project['bugs'], completionList[x]))

        self.ui.search.setCompleter(completer)

        # Здесь нужна лямбда-функция, чтобы предотвратить выполнение closeBug, когда компилятор прогоняет весь код при первом рендеринге
        self.ui.close_bug.clicked.connect(lambda x: self.closeBug(project))
        self.ui.assign.clicked.connect(lambda x: self.selfAssign(project))
        self.ui.deny.clicked.connect(lambda x: self.denyBug(project))

        self.loadMessageHistory()
        self.ui.send.clicked.connect(lambda x: self.sendMessage(project))

        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(getUserInfo('login', login)['image']).content)
        self.ui.users_photo.setIcon(QtGui.QIcon(pixmap))
        self.ui.users_photo.setIconSize(QSize(40, 40))

    def loadBugInfo(self, bugs, bid):
        bug = list(filter(lambda x: x['bid'] == bid, bugs))[0]
        self.bug = bug
        self.bid = bug['bid']
        self.loadMessageHistory()

        # Чтобы не перезаписывать весь сайдбар и не тратить на это время, переписываются только стили
        for x in self.ui.scrollArea.findChildren(QPushButton):
            x.setStyleSheet('')
            if x.property('bid') != self.bid:
                x.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align: left;}QPushButton:hover{background:#322F6E;border-radius: 10px;}')
            else:
                x.setStyleSheet('QPushButton{color:#7D79A5;font-size:15px;padding:7px;border:none;text-align:left;border-radius: 10px;background:#322F6E}')

        self.ui.setWindowTitle(f"Багтрекер - {self.bug['title']}")

        if self.bug['criticality'] == 'high':
            self.ui.criticality.setStyleSheet(config.Config.CriticalBug)
        elif self.bug['criticality'] == 'medium':
            self.ui.criticality.setStyleSheet(config.Config.MediumBug)
        elif self.bug['criticality'] == 'low':
            self.ui.criticality.setStyleSheet(config.Config.NonCriticalBug)
        if self.bug['pastebin_link']:
            self.ui.open_pastebin.setText('Открыть')
            self.ui.open_pastebin.clicked.connect(lambda x: webbrowser.open(self.bug['pastebin_link']))
            self.ui.open_pastebin.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
        else:
            self.ui.open_pastebin.setText('Ссылка не прикреплена')
            self.ui.open_pastebin.setCursor(QCursor(QtCore.Qt.ArrowCursor))

        self.ui.title.setText(self.bug['title'])
        self.ui.description.setText(self.bug['description'])
        self.ui.actual_result.setText(self.bug['actual_result'])
        self.ui.supposed_result.setText(self.bug['supposed_result'])
        self.ui.reproduction.setText(self.bug['steps'])
        self.ui.tags.setText(', '.join([x for x in self.bug['tags']]))
        self.ui.creationDate.setText(datetime.datetime.utcfromtimestamp(self.bug['creationDate'] / 1000).strftime('%d.%m.%Y %H:%M'))
        self.ui.author.setText(getUserInfo('uid', self.bug['author'])['login'])
        self.ui.assignee.setText(getUserInfo('uid', self.bug['assignee'])['login'] if str(self.bug['assignee']).isdigit() else 'Нет')
        self.ui.deadline.setText(str(self.bug['deadline']))

        if self.bug['closed']:
            self.ui.closed.setText(datetime.datetime.utcfromtimestamp(self.bug['closedDate'] / 1000).strftime('%d.%m.%Y %H:%M'))
            # Зачеркивание текста
            self.ui.title.setStyleSheet('color:white;font-weight:bold;font-size:20px;text-decoration:line-through;')
        else:
            self.ui.title.setStyleSheet('color:white;font-weight:bold;font-size:20px;')
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

        self.clearLayout(self.ui.messages.layout())

    def closeBug(self, project):
        for bug in project['bugs']:
            if bug['bid'] == self.bid:
                selected_bug = bug.copy()
                bug['closed'] = True
                # 10800 - 3 часа в секундах, чтобы от UTC перейти к московскому времени
                bug['closedDate'] = round(time.time() + 10800) * 1000
                bug['messages'].append({
                    "author": self.uid,
                    "date": round((time.time() + 10800) * 1000),
                    "text": "<i>Закрыл баг</i>"
                })

        if str(project['owner']).startswith('t_'):
            team = teams.find_one({"tid": project['owner']})
            admin = getUserInfo('uid', team['admin'])

            author = getUserInfo("uid", self.uid)
            subject = f'Изменение статуса бага'
            content = f'{author["login"]} закрыл баг <b>{selected_bug["title"]}</b> в проекте {project["title"]}' \
                      f'<img src="{author["image"]} width="50" height="50"/>'

            # Уведомление о закрытии приходит только админу. Другим, мне кажется, это не нужно
            if admin['notifications']['new_bugs']:
                mailer.sendMail(admin['email'],
                                subject,
                                f'{content}')

        projects.update_one({'title': project['title']}, {'$set': {'bugs': project['bugs']}})
        self.loadBugInfo(project['bugs'], self.bid)
        self.loadBugs(project)
        self.loadMessageHistory()

    def selfAssign(self, project):
        for bug in project['bugs']:
            if bug['bid'] == self.bid:
                selected_bug = bug.copy()
                bug['assignee'] = self.uid
                bug['messages'].append({
                    "author": self.uid,
                    "date": round((time.time() + 10800) * 1000),
                    "text": "<i>Закрепил баг за собой</i>"
                })

        if str(project['owner']).startswith('t_'):
            team = teams.find_one({"tid": project['owner']})
            admin = getUserInfo('uid', team['admin'])

            author = getUserInfo("uid", self.uid)
            subject = f'Изменение статуса бага'
            content = f'{author["login"]} закрепил за собой баг <b>{selected_bug["title"]}</b> в проекте {project["title"]}' \
                      f'<img src="{author["image"]} width="50" height="50"/>'

            # Уведомление приходит только админу
            if admin['notifications']['new_bugs']:
                mailer.sendMail(admin['email'],
                                subject,
                                f'{content}')

        projects.update_one({'title': project['title']}, {'$set': {'bugs': project['bugs']}})
        self.loadBugInfo(project['bugs'], self.bid)
        self.loadBugs(project)
        self.loadMessageHistory()

    def denyBug(self, project):
        for bug in project['bugs']:
            if bug['bid'] == self.bid:
                selected_bug = bug
                bug['assignee'] = 'Нет'
                bug['messages'].append({
                    "author": self.uid,
                    "date": round((time.time() + 10800) * 1000),
                    "text": "<i>Отказался от бага</i>"
                })

        if str(project['owner']).startswith('t_'):
            team = teams.find_one({"tid": project['owner']})
            admin = getUserInfo('uid', team['admin'])

            author = getUserInfo("uid", self.uid)
            subject = f'Изменение статуса бага'
            content = f'{author["login"]} отказался от бага <b>{selected_bug["title"]}</b>' \
                      f'<img src="{author["image"]} width="50" height="50"/>'

            if admin['notifications']['new_bugs']:
                mailer.sendMail(admin['email'],
                                subject,
                                f'{content}')

            for x in team['members']:
                user = getUserInfo('uid', x)
                if user['notifications']['new_bugs']:
                    mailer.sendMail(user['email'],
                                    subject,
                                    f'{content}')

        projects.update_one({'title': project['title']}, {'$set': {'bugs': project['bugs']}})
        self.loadBugInfo(project['bugs'], self.bid)
        self.loadBugs(project)
        self.loadMessageHistory()

    def loadMessageHistory(self):
        self.clearLayout(self.ui.messages.layout())

        if self.bug['messages']:
            layout = QVBoxLayout()
            layout.setAlignment(Qt.AlignTop)
            for message in self.bug['messages']:
                author = f"<b>{getUserInfo('uid', message['author'])['login']}</b>" if message['author'] == self.uid else f"{getUserInfo('uid', message['author'])['login']}"
                item = QLabel(f"{datetime.datetime.utcfromtimestamp(message['date'] / 1000).strftime('%d.%m.%Y %H:%M')} {author}: {' '.join(message['text'].split())}")
                item.setStyleSheet('color: #fff;')
                layout.addWidget(item)

            widget = QWidget()
            widget.setLayout(layout)
            self.ui.messages.setWidget(widget)
        # Если переключиться на баг, где нет сообщений, остаются фантомные сообщения с другого бага
        elif len(self.bug['messages']) == 0:
            self.clearLayout(self.ui.messages.layout())

    def sendMessage(self, project):
        if self.ui.message.toPlainText() not in ['Отказался от бага', 'Хочет выполнить задачу', 'Закрепил баг за собой']:
            bugs = project['bugs']
            for bug in bugs:
                if bug['bid'] == self.bid:
                    bug['messages'].append({
                        "author": self.uid,
                        "date": round((time.time() + 10800) * 1000),
                        "text": self.ui.message.toPlainText()
                    })
                    selected_bug = bug.copy()

            if str(project['owner']).startswith('t_'):
                team = teams.find_one({"tid": project['owner']})
                admin = getUserInfo('uid', team['admin'])

                created_message = selected_bug['messages'][-1].copy()
                author = getUserInfo("uid", self.uid)
                subject = f'Новое сообщение от {author["login"]}'
                content = f'<h2>Сообщение в "{bug["title"]}"</h2><br><br>' \
                          f'{datetime.datetime.now(pytz.timezone("Europe/Moscow")).strftime("%d %B, %H:%M:%S")}: {author["login"]} - {created_message["text"]}' \
                          f'<img src="{author["image"]} width="50" height="50"/>'

                if admin['notifications']['new_bugs']:
                    mailer.sendMail(admin['email'],
                                    subject,
                                    f'{content}')

                for x in team['members']:
                    user = getUserInfo('uid', x)
                    if user['notifications']['new_bugs']:
                        mailer.sendMail(user['email'],
                                        subject,
                                        f'{content}')


            projects.update_one({"title": project['title']}, {'$set': {'bugs': bugs}})

        self.ui.message.setPlainText('')
        self.loadMessageHistory()

    def show(self):
        self.ui.show()

    def goToMainPage(self):
        from main_page import MainPage

        self.ui.hide()
        self.ui = MainPage(self.uid, self.login, referrer_project=self.project)
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
            if not bug['closed']:
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
                bugInList.clicked.connect(self.partial)
                layout.addWidget(bugInList)

        widget = QWidget()
        widget.setLayout(layout)
        self.ui.scrollArea.setWidget(widget)

    def partial(self):
        sender = self.sender()
        self.loadBugInfo(self.project['bugs'], sender.property('bid'))

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

        for tag in range(len(self.project['tags'])):
            self.ui_create_card.tags.addItem(self.project['tags'][tag]['name'])
        self.ui_create_card.tags.addItem('+ Создать новый')

        criticalityLevel = ["Низкая", "Средняя", "Высокая"]
        for crit in criticalityLevel:
            self.ui_create_card.criticality.addItem(crit)

        self.ui_create_card.assignee.addItem("Нет")

        self.ui_create_card.assignee.addItem(self.login)
        if str(self.project['owner']).startswith('t_'):
            certainTeam = teams.find_one({'tid': self.project['owner']})
            members = certainTeam['members']

            for user_id in members:
                self.ui_create_card.assignee.addItem(users.find_one({'uid': user_id})['login'])

            if certainTeam['admin'] != getUserInfo('login', self.login)['uid']:
                self.ui_create_card.assignee.setEnabled(False)

        else:
            certainTeam = getUserTeam(self.project['owner'])

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
        from main_page import backgrounds
        styles = random.choice(backgrounds)

        if self.ui_create_card.assignee.currentText() == 'Нет':
            assignee = 'Нет'
        else:
            assignee = getUserInfo('login', self.ui_create_card.assignee.currentText())['uid']

        deadline = datetime.datetime.strptime(self.ui_create_card.deadline.date().toString('yyyy.MM.dd'), '%Y.%m.%d').strftime("%d.%m.%Y")

        # Массив тегов должен заполняться всеми выбранными в дропдауне элементами
        tags = [self.ui_create_card.tags.currentText()]

        project = self.project
        project['bugs'].append({
            "bid": "b_" + str(random.randrange(111111, 999999, 5)),
            "title": self.ui_create_card.title.text(),
            "description": self.ui_create_card.description.toPlainText(),
            "actual_result": self.ui_create_card.actual_result.toPlainText(),
            "supposed_result": self.ui_create_card.supposed_result.toPlainText(),
            "creationDate": round(time.time() * 1000),
            "author": getUserInfo('login', self.login)['uid'],
            "assignee": assignee,
            "deadline": deadline,
            "criticality": criticality,
            "tags": tags,
            "closed": False,
            # Фон и цвет текста карточки
            "styles": styles,
            "steps": self.ui_create_card.reproduction.toPlainText(),
            "complexity": self.ui_create_card.horizontalSlider.value(),
            "messages": [],
            "pastebin_link": pbp.paste(os.environ.get('PASTEBIN_KEY'), self.ui_create_card.code_fragment.toPlainText(), self.ui_create_card.title.text(), privacy="1") if self.ui_create_card.code_fragment.toPlainText() else ""


        })

        # Отправка писем о новых багах всем участникам проекта
        # Рассылка запустится только если это командный проект. Зачем уведомления в индивидуальном проекте, если там один человек
        if str(project['owner']).startswith('t_'):
            team = teams.find_one({"tid": project['owner']})
            admin = getUserInfo('uid', team['admin'])

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
                user = getUserInfo('uid', x)
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

    def reloadProjectInfo(self):
        self.goToMainPage()

    def goToSettingsPage(self):
        from settings_page import SettingPage

        self.ui.hide()
        self.ui = SettingPage(self.uid, self.login)
        self.ui.show()

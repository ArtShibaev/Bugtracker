import hashlib
import re
import requests
import os

from PySide6.QtGui import QPixmap
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import *
from pymongo import MongoClient

from dotenv import load_dotenv
from image_loader import Images

load_dotenv('.env')

MONGO_URL = "mongodb+srv://ra1nbow1:ra1nbow1@rbs.ftmj9.mongodb.net/rbs"

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
    elif type == "uid":
        user = users.find_one({"uid": value})
    else:
        user = None
    return user


def mailValidation(new_mail):
    if re.fullmatch(re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'), new_mail):
        return 'Письмо с подтверждением отправлено на почту'
    else:
        return 'Некорректно указана почта'


class SettingPage(QtCore.QObject):
    def __init__(self, uid, login):
        super().__init__()
        self.ui = loader.load('./interfaces/settings_page.ui', None)

        self.login = login
        self.uid = uid
        self.pixmap = QPixmap()
        self.ui.Save_mail.clicked.connect(self.mail_changed)
        self.ui.Save_password.clicked.connect(self.password_c)
        self.ui.home.clicked.connect(self.goToMainPage)
        self.ui.Not_button.clicked.connect(self.goToNotificationsSettings)
        self.ui.Mail_s.hide()
        self.ui.Password_c.hide()

        self.ui.logout.clicked.connect(self.logout)

        Images.load_image(self, 'settings_page')

        pixmap = QPixmap()
        pixmap.loadFromData(requests.get(getFullUserInfo('login', self.login)['image']).content)
        self.ui.Avatarka.setIcon(QtGui.QIcon(pixmap))
        self.ui.Avatarka.setIconSize(QSize(300, 300))

    def show(self):
        self.ui.show()

    def mail_changed(self):
        new_mail = self.ui.Input_mail.text()
        self.ui.Mail_s.show()
        self.ui.Mail_s.setText(mailValidation(new_mail))

    def password_c(self):
        password1 = self.ui.Input_password.text()
        password2 = self.ui.Input_password2.text()

        if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password1) is None:
            message = 'Пароль не удовлетворяет требованиям'
            self.ui.Password_c.setStyleSheet('QPushButton{color:rgba(255,0,0,0.75);background-color:rgba(255, 0, 0, 0.2);font-size:15px;height:45px;width:300px;}QPushButton:hover{background-color:rgba(255,0,0,0.1);border-radius:10px;}')
        elif (password1 != password2) or (not password2):
            self.ui.Password_c.setStyleSheet('QPushButton{color:rgba(255,0,0,0.75);background-color:rgba(255, 0, 0, 0.2);font-size:15px;height:45px;width:300px;}QPushButton:hover{background-color:rgba(255,0,0,0.1);border-radius:10px;}')
            message = "Пароли не совпадают!"
        else:
            message = 'Пароль успешно изменен!'

            users.update_one({'uid': self.uid}, {'$set': {'password': hashlib.sha256(password1.encode('utf-8')).hexdigest()}})

            self.ui.Password_c.setStyleSheet('QPushButton{color: #34B132;background-color: rgba(52,177,20,0.26);font-size: 15px;height: 45px;width: 200px;}QPushButton:hover{background-color: rgba(52, 140, 20, 0.26);border-radius: 10px;}')
            self.ui.Input_password.setText('')
            self.ui.Input_password2.setText('')

        self.ui.Password_c.setText(message)
        self.ui.Password_c.show()

    def goToMainPage(self):
        from main_page import MainPage
        self.ui.hide()
        self.ui = MainPage(self.uid, self.login)
        self.ui.show()

    def logout(self):
        from login_form import LoginForm
        self.ui.hide()
        self.ui = LoginForm()
        self.ui.show()

    def goToNotificationsSettings(self):
        from settings_page_not import SettingPageNot
        self.ui.hide()
        self.ui = SettingPageNot(self.uid, self.login)
        self.ui.show()

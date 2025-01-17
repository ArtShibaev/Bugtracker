import hashlib
import random
import re
import requests
import os

from PySide6.QtGui import QPixmap
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import *
from pymongo import MongoClient
from urllib import request

from dotenv import load_dotenv
from image_loader import Images
from mailer import sendMail

load_dotenv('.env')

MONGO_URL = "ССЫЛКА БД"

loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']
teams = db['teams']
# image = db['image']



def getFullUserInfo(type, value):
    if type == "login":
        user = users.find_one({"login": value})
    elif type == "uid":
        user = users.find_one({"uid": value})
    else:
        user = None
    return user



class SettingPage(QtCore.QObject):
    def __init__(self, uid, login):
        super().__init__()
        self.ui = loader.load('./interfaces/settings_page.ui', None)

        self.login = login
        self.uid = uid
        self.pixmap = QPixmap()
        self.ui.Save_mail.clicked.connect(lambda: self.verification(self.mail_changed))
        self.ui.Save_password.clicked.connect(lambda: self.verification(self.password_c))
        self.ui.home.clicked.connect(self.goToMainPage)
        self.ui.Not_button.clicked.connect(self.goToNotificationsSettings)
        self.ui.Mail_s.hide()
        self.ui.Fail_ver.hide()
        self.ui.Password_c.hide()
        self.ui.verification_code.hide()
        self.ui.submit_verification_code.hide()
        self.ui.Url_exeption.hide()
        self.ui.submit_verification_code.clicked.connect(self.submitVerificationCode)
        self.ui.UrlChange.clicked.connect(self.url_change)
        self.ui.logout.clicked.connect(self.logout)

        Images.load_image(self, 'settings_page')

        pixmap = QPixmap()
        try:
            pixmap.loadFromData(requests.get(getFullUserInfo('login', self.login)['image']).content)
        except requests.exceptions.MissingSchema:
            url = 'https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png'
            pixmap.loadFromData(request.urlopen(url).read())
            self.ui.Url_exeption.show()
        self.ui.Avatarka.setIcon(QtGui.QIcon(pixmap))
        self.ui.Avatarka.setIconSize(QSize(300, 300))


    def show(self):
        self.ui.show()

    def verification(self, field):
        if getFullUserInfo('login', self.login)['password'] == hashlib.sha256(self.ui.Pass_ver.text().encode('utf-8')).hexdigest():
            self.ui.Fail_ver.hide()
            self.ui.Fail_ver.setText('')
            field()
        else:
            self.ui.Fail_ver.show()


    def mail_changed(self):
        self.new_mail = self.ui.Input_mail.text()

        if re.fullmatch(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', self.new_mail) and self.new_mail != getFullUserInfo('uid', self.uid)['email']:
            self.code = str(random.randrange(111111, 999999, 6))
            sendMail(self.new_mail, 'Подтверждение почтового адреса', f'Ваш проверочный код: {self.code}')
            self.ui.Mail_s.setStyleSheet('QPushButton{color: #34B132;background-color: rgba(52,177,20,0.26);font-size: 15px;height: 45px;width: 350px;}QPushButton:hover{background-color: rgba(52, 140, 20, 0.26);border-radius: 10px;}')
            message = 'Письмо с подтверждением отправлено на почту'
            self.ui.Input_mail.setText('')
            self.ui.verification_code.show()
            self.ui.submit_verification_code.show()
        else:
            self.ui.Mail_s.setStyleSheet('QPushButton{color:rgba(255,0,0,0.75);background-color:rgba(255, 0, 0, 0.2);font-size:15px;height:45px;width:350px;}QPushButton:hover{background-color:rgba(255,0,0,0.1);border-radius:10px;}')
            message = 'Некорректно указана почта'

        self.ui.Mail_s.show()
        self.ui.Mail_s.setText(message)

    def submitVerificationCode(self):
        if self.ui.verification_code.text() == self.code:
            self.ui.Mail_s.setText('Почта изменена')
            self.ui.Mail_s.setStyleSheet('QPushButton{color: #34B132;background-color: rgba(52,177,20,0.26);font-size:15px;height:45px;width:200px;}QPushButton:hover{background-color: rgba(52, 140, 20, 0.26);border-radius: 10px;}')
            self.ui.Mail_s.show()
            users.update_one({'uid': self.uid}, {'$set': {'email': self.new_mail}})

            self.code = None
            self.new_mail = None
            self.ui.verification_code.setText('')
            self.ui.verification_code.hide()
            self.ui.submit_verification_code.hide()
        else:
            self.ui.Mail_s.setText('Неверный код')
            self.ui.Mail_s.setStyleSheet('QPushButton{color:rgba(255,0,0,0.75);background-color:rgba(255, 0, 0, 0.2);font-size:15px;height:45px;width:200px;}QPushButton:hover{background-color:rgba(255,0,0,0.1);border-radius:10px;}')
            self.ui.Mail_s.show()

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

    def url_change(self):
        link = self.ui.Image_link.text()
        users.update_one({'uid': self.uid}, {'$set': {'image': link}})
        self.ui.Url_exeption.hide()

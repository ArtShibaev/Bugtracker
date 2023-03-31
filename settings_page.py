import re
import requests
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import *
from pymongo import MongoClient



import os

from dotenv import load_dotenv
from image_loader import Images


load_dotenv('.env')

MONGO_URL="mongodb+srv://ra1nbow1:ra1nbow1@rbs.ftmj9.mongodb.net/rbs"

loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']
teams = db['teams']

mail_pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')



def Mail_valid(new_mail):
    if re.fullmatch(mail_pattern, new_mail):
        return 'Письмо с подтверждением отправлено на почту'
    else:
        return 'Некорректно указана почта'


URL =' https://steamuserimages-a.akamaihd.net/ugc/1842548410823874095/EF62A9435943C812CEF0E2F347CC110B7AB0074D/?imw=512&amp;imh=512&amp;ima=fit&amp;impolicy=Letterbox&amp;imcolor=%23000000&amp;letterbox=true'


class SettingPage(QtCore.QObject):
    def __init__(self, uid, login):
        super().__init__()
        self.ui = loader.load('./interfaces/settings_page.ui', None)

        self.user_login = login
        self.uid = uid

        self.pixmap = QPixmap()
        self.Set_url_image(URL)

        self.ui.show()
        self.ui.Save_mail.clicked.connect(self.mail_changed)
        self.ui.Save_password.clicked.connect(self.password_c)
        self.ui.home.clicked.connect(self.GoToMainPage)
        self.ui.Mail_s.hide()
        self.ui.Password_c.hide()

    def mail_changed(self):
        new_mail = self.ui.Input_mail.text()
        self.ui.Mail_s.show()
        self.ui.Mail_s.setText(Mail_valid(new_mail))

    def password_c(self):
        message = 'Пароль успешно изменен!'
        password1 = self.ui.Input_password.text()
        password2 = self.ui.Input_password2.text()
        if password1 != password2:
            message = "Пароли не совпадают!"
        if len(password1) < 1 or len(password2) < 1:
            message = "Введите пароль"
        self.ui.Password_c.show()
        self.ui.Password_c.setText(message)

    def Set_url_image(self, imageURL):
        request = requests.get(imageURL)
        self.pixmap.loadFromData(request.content)
        # self.ui.Avatarka.setPixmap(QtGui.QPixmap(self.pixmap))
        # self.ui.pushButton.setIcon(QtGui.QIcon(self.pixmap))
        # self.ui.pushButton.setIconSize(QSize(201, 201))

    def GoToMainPage(self):
        from main_page import MainPage
        self.ui.hide()
        self.ui = MainPage(self.uid, self.user_login)
        self.ui.show()

    def logout(self):
        from login_form import LoginForm
        self.ui.hide()
        self.ui = LoginForm()
        self.ui.show()
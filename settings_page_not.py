import requests
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import *
from pymongo import MongoClient

# хуй

import os

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


class SettingPageNot(QtCore.QObject):
    def __init__(self, uid, login):
        super().__init__()
        self.ui = loader.load('./interfaces/settings_page_not.ui', None)

        self.login = login
        self.uid = uid
        self.ui.show()
        self.ui.logout.clicked.connect(self.logout)
        self.ui.home.clicked.connect(self.goToMainPage)
        self.ui.Account_settings.clicked.connect(self.goToAccountSettings)

    def show(self):
        self.ui.show()

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

    def goToAccountSettings(self):
        from settings_page import SettingPage
        self.ui.hide()
        self.ui = SettingPage(self.uid, self.login)
        self.ui.show()
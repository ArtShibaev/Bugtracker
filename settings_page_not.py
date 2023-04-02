from PySide6.QtWidgets import QCheckBox
from PySide6 import QtCore, QtGui
from PySide6.QtUiTools import QUiLoader
from pymongo import MongoClient

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
        self.ui.Save_checkbox.clicked.connect(self.Save_checkbox)
        self.ui.home.clicked.connect(self.goToMainPage)
        self.ui.Account_settings.clicked.connect(self.goToAccountSettings)
        Images.load_image(self, 'settings_notifications_page')
        self.checkbox()

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

    def checkbox(self):
        check = users.find_one({"login": self.login})['notifications']
        for element in check: self.ui.frame_5.findChild(QCheckBox, name=element).setChecked(check[element])

    def Save_checkbox(self):
        check = users.find_one({"login": self.login})['notifications']
        check['new_bugs'] = self.ui.new_bugs.isChecked()
        check['new_comments'] = self.ui.new_comments.isChecked()
        check['status_changes'] = self.ui.status_changes.isChecked()

        users.update_one({"login": self.login}, {'$set': {'notifications': check}})

from PySide6 import QtCore, QtGui
from PySide6.QtUiTools import QUiLoader
from pymongo import MongoClient

import hashlib
import os
from dotenv import load_dotenv

from registration_form import RegistrationForm
from main_page import MainPage
from config import Config as styles

load_dotenv('.env')


loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']

def findUser(login):
    user = users.find_one({'login': login})
    return user

# Функция возвращает все проекты, которые есть у пользователя
def findOwnedProjects(uid):
    result = projects.find_one({'owner': uid})
    return result

class LoginForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/login_form.ui', None)

        self.ui.show_password.stateChanged.connect(self.showHidePassword)
        self.ui.login_button.clicked.connect(self.login)
        self.ui.register_button.clicked.connect(self.goToRegistration)
        self.ui.show_password.setStyleSheet("QCheckBox::indicator{ width :30px; height :30px; image: url(./images/eye-close.png); }")
    def show(self):
        self.ui.show()

    def login(self):

        self.ui.input_login.setStyleSheet(styles.DefaultBorder)
        self.ui.input_password.setStyleSheet(styles.DefaultBorder)

        current_user = findUser(self.ui.input_login.text())

        # Проверка на нахождения логина в базе данных
        if current_user is None:
            self.ui.input_login.setStyleSheet(styles.RedBorder)
        if not self.ui.input_password.text():
            self.ui.input_password.setStyleSheet(styles.RedBorder)
        elif current_user['password'] == hashlib.sha256(self.ui.input_password.text().encode('utf-8')).hexdigest():
             if findOwnedProjects(current_user['uid']) is not None:
                 print('У юзера есть проекты')
                 self.ui.hide()
                 self.ui = MainPage(current_user['uid'])
                 self.ui.show()
             else:
                 self.goToWelcomePage()
        else:
            self.ui.input_password.setStyleSheet(styles.RedBorder)


    def showHidePassword(self):
        if self.ui.show_password.isChecked():
            self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Normal);
            self.ui.show_password.setStyleSheet("QCheckBox::indicator:checked{ width :30px; height :30px; image: url(./images/eye-open.png); }")
        else:
            self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password);
            self.ui.show_password.setStyleSheet("QCheckBox::indicator:unchecked{ width :30px; height :30px; image: url(./images/eye-close.png); }")

    def goToRegistration(self):
        # Скрываем интерфейс логина
        self.ui.hide()
        # Переопределяем интерфейс на регистрацию
        self.ui = RegistrationForm()
        self.ui.show()

    def goToWelcomePage(self):
        from welcome_page_form import WelcomePageForm
        self.ui.hide()
        self.ui = WelcomePageForm(self.ui.input_login.text())
        self.ui.show()
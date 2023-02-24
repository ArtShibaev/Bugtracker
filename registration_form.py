from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader

from dotenv import load_dotenv
from pymongo import MongoClient

import re
import time
import hashlib
import os
import random
from config import Config as styles

load_dotenv('.env')

loader = QUiLoader()

mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']

def find_user(login):
    user = users.find_one({'login': login})
    return user

class RegistrationForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/registration_form.ui', None)
        self.ui.submit_button.clicked.connect(self.register)
        self.ui.login_button.clicked.connect(self.goToLogin)

    def show(self):
        self.ui.show()

    def validator(self):
        # При каждом нажатии кнопки нормализуем все цвета бордера
        self.ui.input_login.setStyleSheet(styles.DefaultBorder)
        self.ui.input_email.setStyleSheet(styles.DefaultBorder)
        self.ui.input_password.setStyleSheet(styles.DefaultBorder)
        self.ui.input_password_repeat.setStyleSheet(styles.DefaultBorder)

        flag = True

        # Проверка, если такой логин уже существует
        if find_user(self.ui.input_login.text()) is not None:
            self.ui.input_login.setStyleSheet(styles.RedBorder)
            self.ui.input_login.setText('Логин занят')
            flag = False

        # Валидация логина
        if re.match(r'^(?=.*[A-Za-z0-9]$)[A-Za-z][A-Za-z\d.-]{0,19}$', self.ui.input_login.text()) is None:
            self.ui.input_login.setStyleSheet(styles.RedBorder)
            flag = False
        # Валидация почты - x@x.xx
        if re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', self.ui.input_email.text()) is None:
            self.ui.input_email.setStyleSheet(styles.RedBorder)
            flag = False
        # Валидация пароля - 8 символов, минимум одна буква, минимум одна цифра
        if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', self.ui.input_password.text()) is None:
            self.ui.input_password.setStyleSheet(styles.RedBorder)
            flag = False
        # Валидация повторного пароля - если он не совпадает или пустой
        if (self.ui.input_password.text() != self.ui.input_password_repeat.text()) or (not self.ui.input_password_repeat.text()):
            self.ui.input_password_repeat.setStyleSheet(styles.RedBorder)
            flag = False

        return flag

    def register(self):
        if self.validator():
            users.insert_one({
                "login": self.ui.input_login.text(),
                "password": hashlib.sha256(self.ui.input_password.text().encode('utf-8')).hexdigest(),
                "email": self.ui.input_email.text(),
                "registrationDate": round(time.time()*1000),
                "uid": random.randrange(111111, 999999, 6),
            })
            # После регистрации у юзера точно не будет никаких проектов, поэтому он всегда будет переходить на пустую страницу
            self.goToWelcomePage()

    def goToLogin(self):
        from login_form import LoginForm
        self.ui.hide()
        self.ui = LoginForm()
        self.ui.show()

    def goToWelcomePage(self):
        from welcome_page_form import WelcomePageForm
        self.ui.hide()
        self.ui = WelcomePageForm(self.ui.input_login.text())
        self.ui.show()

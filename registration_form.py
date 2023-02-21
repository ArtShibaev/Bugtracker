from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader

from dotenv import load_dotenv
from pymongo import MongoClient

import re
import time
import hashlib
import os

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
    Style = "QLineEdit{ border: 2px solid #373C66; color: white; border-radius: 15px; padding: 5px 10px;outline: none; } QLineEdit:focus{ border-color: #947E45; }"
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/registration_form.ui', None)
        self.ui.submit_button.clicked.connect(self.register)
        self.ui.login_button.clicked.connect(self.goToLogin)

    def show(self):
        self.ui.show()

    def validator(self):
        # При каждом нажатии кнопки нормализуем все цвета бордера
        self.ui.input_login.setStyleSheet(RegistrationForm.Style)
        self.ui.input_email.setStyleSheet(RegistrationForm.Style)
        self.ui.input_password.setStyleSheet(RegistrationForm.Style)
        self.ui.input_password_repeat.setStyleSheet(RegistrationForm.Style)

        flag = True

        # Проверка, если такой логин уже существует
        if find_user(self.ui.input_login.text()) is not None:
            self.setBorderColor(self.ui.input_login, 'red')
            self.ui.input_login.setText('Логин занят')
            flag = False

        # Валидация логина
        if re.match(r'^(?=.*[A-Za-z0-9]$)[A-Za-z][A-Za-z\d.-]{0,19}$', self.ui.input_login.text()) is None:
            self.setBorderColor(self.ui.input_login, 'red')
            flag = False
        # Валидация почты - x@x.xx
        if re.fullmatch(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', self.ui.input_email.text()) is None:
            self.setBorderColor(self.ui.input_email, 'red')
            flag = False
        # Валидация пароля - 8 символов, минимум одна буква, минимум одна цифра
        if re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', self.ui.input_password.text()) is None:
            self.setBorderColor(self.ui.input_password, 'red')
            flag = False
        # Валидация повторного пароля - если он не совпадает или пустой
        if (self.ui.input_password.text() != self.ui.input_password_repeat.text()) or (not self.ui.input_password_repeat.text()):
            self.setBorderColor(self.ui.input_password_repeat, 'red')
            flag = False

        return flag

    def register(self):
        if self.validator():
            users.insert_one({
                "login": self.ui.input_login.text(),
                # Хэширование пароля
                "password": hashlib.sha256(self.ui.input_password.text().encode('utf-8')).hexdigest(),
                "email": self.ui.input_email.text(),
                # Время в Unix
                "registrationDate": round(time.time()*1000)
            })
            self.ui.close()

    # Функция изменяет цвет границы на color для элемента input
    def setBorderColor(self, input, color):
        input.setStyleSheet('QLineEdit {border: 2px solid ' + color + ';color: white;border-radius: 15px;padding: 5px 10px;outline: none;focus {border-color: rgb(130, 118, 255);}}')



    def goToLogin(self):
        # Да, это импорт посередине кода. Если указать его сверху, то компилятор распознает его как зацикленный
        # Поэтому файл ипортируется только тогда, когда нужно
        # Только это создает полусекундную задержку :(
        from login_form import LoginForm

        self.ui.hide()
        self.ui = LoginForm()
        self.ui.show()
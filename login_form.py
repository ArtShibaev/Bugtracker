import os

from dotenv import load_dotenv

from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from pymongo import MongoClient

from registration_form import RegistrationForm

load_dotenv('.env')


loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')

def find_user(login):
    user = users.find_one({'login': login})

    return user

class LoginForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/login_form.ui', None)

        self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)
        self.ui.show_password.stateChanged.connect(self.showHidePassword)
        self.ui.login_button.clicked.connect(self.login)
        self.ui.register_button.clicked.connect(self.goToRegistration)

    def show(self):
        self.ui.show()
    # Тестовые данные login:pass - 123:321
    def login(self):

        self.setBorderColor(self.ui.input_login, 'gray')
        self.setBorderColor(self.ui.input_password, 'gray')

        current_user = find_user(self.ui.input_login.text())

        # Проверка на нахождения логина в базе данных
        if current_user is None:
            self.setBorderColor(self.ui.input_login, 'red')
        elif current_user['password'] == self.ui.input_password.text():
            print('Выполнен вход')
        else:
            self.setBorderColor(self.ui.input_password, 'red')


    def showHidePassword(self):
        if self.ui.show_password.isChecked(): self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Normal)
        else: self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)

    def setBorderColor(self, input, color):
        input.setStyleSheet('QLineEdit {border: 2px solid ' + color + ';color: white;border-radius: 15px;padding: 5px 10px;outline: none;focus {border-color: rgb(130, 118, 255);}}')

    def goToRegistration(self):
        # Скрываем интерфейс логина
        self.ui.hide()
        # Переопределяем интерфейс на регистрацию
        self.ui = RegistrationForm()
        self.ui.show()
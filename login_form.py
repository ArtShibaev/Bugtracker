import os
from dotenv import load_dotenv

from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from pymongo import MongoClient

load_dotenv('.env')


loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')

def find_user(login):
    client = MongoClient(mongo_url)
    db = client['bugtracker']
    users = db['users']
    user = users.find_one({'login': login})

    return user

class LoginForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('interface.ui', None)

        self.ui.submit_button.clicked.connect(self.login)
        self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)
        self.ui.show_password.stateChanged.connect(self.show_hide_password)
    def show(self):
        self.ui.show()
    # Тестовые данные login:pass - 123:321
    def login(self):
        print(self.ui.input_login.text() + ':' + self.ui.input_password.text())
        current_user = find_user(self.ui.input_login.text())

        # Проверка на нахождения логина в базе данных
        if current_user == None:
            print('Пользователь не найден')
        elif current_user['password'] == self.ui.input_password.text():
            print('Выполнен вход')
        else:
            print('Пароль неверный')

    def show_hide_password(self):
        if self.ui.show_password.isChecked(): self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Normal)
        else: self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)

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
        self.ui_reg = loader.load('registration_page.ui', None)
        self.ui.submit_button.clicked.connect(self.login)
        self.ui_reg.submit_button_registration.clicked.connect(self.registration_data)
        self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)
        self.ui.show_password.stateChanged.connect(self.show_hide_password)
    def show(self):
        self.ui.show()
        self.ui_reg.show()
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
    def registration_data(self):
        login = self.ui_reg.input_login_registration
        password = self.ui_reg.input_password_registration
        password_sec = self.ui_reg.input_password_registration_second_time
        if login.text() == '': login.setPlaceholderText("Введите логин!")
        if password.text() != password_sec.text(): password_sec.setText(''); password_sec.setPlaceholderText("Пароли не совпадают!")
        elif password.text() == '': password.setPlaceholderText("Введите пароль!")
        else: print('Данные пользвателя: ' + login.text() + ':' + password.text()); self.ui_reg.close()

    def show_hide_password(self):
        if self.ui.show_password.isChecked(): self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Normal)
        else: self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)

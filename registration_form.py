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

class RegistrationForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('registration_page.ui', None)
        self.ui.submit_button_registration.clicked.connect(self.registration_data)
    def show(self):
        self.ui.show()
    def registration_data(self):
        login = self.ui.input_login_registration
        password = self.ui.input_password_registration
        password_sec = self.ui.input_password_registration_second_time
        if login.text() == '': login.setPlaceholderText("Введите логин!")
        if password.text() != password_sec.text(): password_sec.setText(''); password_sec.setPlaceholderText("Пароли не совпадают!")
        elif password.text() == '': password.setPlaceholderText("Введите пароль!")
        else: print('Данные пользователя: ' + login.text() + ':' + password.text()); self.ui.close()

    def goToLogin(self):
        # Да, это импорт посередине кода. Если указать его сверху, то компилятор распознает его как зацикленный
        # Поэтому файл ипортируется только тогда, когда нужно
        from login_form import LoginForm

        self.ui.hide()
        self.ui = LoginForm()
        self.ui.show()
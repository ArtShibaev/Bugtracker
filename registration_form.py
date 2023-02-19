from PySide6 import QtCore
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtUiTools import QUiLoader
import re

loader = QUiLoader()

class RegistrationForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/registration_form.ui', None)
        self.ui.submit_button.clicked.connect(self.register)
    def show(self):
        self.ui.show()
    def register(self):
        if self.validator():
            print('Данные пользователя: ' + f'login: {self.ui.input_login.text()}, email: {self.ui.input_email.text()}, pass: {self.ui.input_password.text()}')
            self.ui.close()

    # Функция изменяет цвет границы на color для элемента input
    def setBorderColor(self, input, color):
        input.setStyleSheet('QLineEdit {border: 2px solid ' + color + ';color: white;border-radius: 15px;padding: 5px 10px;outline: none;focus {border-color: rgb(130, 118, 255);}}')

    def validator(self):
        # При каждом нажатии кнопки нормализуем все цвета бордера
        self.setBorderColor(self.ui.input_login, 'gray')
        self.setBorderColor(self.ui.input_email, 'gray')
        self.setBorderColor(self.ui.input_password, 'gray')
        self.setBorderColor(self.ui.input_password_repeat, 'gray')

        flag = True

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

    def goToLogin(self):
        # Да, это импорт посередине кода. Если указать его сверху, то компилятор распознает его как зацикленный
        # Поэтому файл ипортируется только тогда, когда нужно
        from login_form import LoginForm

        self.ui.hide()
        self.ui = LoginForm()
        self.ui.show()
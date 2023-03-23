import os
import sys
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from dotenv import load_dotenv

load_dotenv('.env')

loader = QUiLoader()


class SettingPage(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/settings.ui', None)
        self.ui.show()
        self.ui.Save_mail.clicked.connect(self.mail_changed)
        self.ui.Save_password.clicked.connect(self.password_c)
        self.ui.Mail_s.hide()
        self.ui.Password_c.hide()

    def mail_changed(self):
        new_mail = self.ui.Input_mail.text()
        if new_mail == '':
            self.ui.Mail_s.show()
            self.ui.Mail_s.setText('Введите почту!')
        else:
            self.ui.Mail_s.show()
            self.ui.Mail_s.setText(f'Письмо с подтверждением отправлено на адрес {new_mail}')

    def password_c(self):
        message = 'Пароль успешно изменен!'
        password1 = self.ui.Input_password.text()
        password2 = self.ui.Input_password2.text()
        if password1 != password2:
            message = "Пароли не совпадают!"
        self.ui.Password_c.show()
        self.ui.Password_c.setText(message)






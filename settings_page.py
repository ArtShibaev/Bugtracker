import os
import sys
from PySide6 import QtWidgets
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from dotenv import load_dotenv
import re

load_dotenv('.env')

loader = QUiLoader()

mail_pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def Mail_valid(new_mail):
    if re.fullmatch(mail_pattern, new_mail):
        return 'Письмо с подтверждением отправлено на почту'
    else:
        return 'Некорректно указана почта'


class SettingPage(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/settings1.ui', None)
        self.ui.show()
        self.ui.Save_mail.clicked.connect(self.mail_changed)
        self.ui.Save_password.clicked.connect(self.password_c)
        self.ui.Mail_s.hide()
        self.ui.Password_c.hide()
        self.ui.Mail_notebutton.hide()
        self.ui.Pass_notebutton.hide()

    def mail_changed(self):
        new_mail = self.ui.Input_mail.text()
        self.ui.Mail_s.show()
        self.ui.Mail_s.setText(Mail_valid(new_mail))

    def password_c(self):
        message = 'Пароль успешно изменен!'
        password1 = self.ui.Input_password.text()
        password2 = self.ui.Input_password2.text()
        if password1 != password2:
            message = "Пароли не совпадают!"
        if len(password1) <1 or len(password2) < 1:
            message = "Введите пароль"
        self.ui.Password_c.show()
        self.ui.Password_c.setText(message)






from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

class RegistrationForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/registration_form.ui', None)
        # На кнопку привязан редирект на логин для теста
        self.ui.submit_button.clicked.connect(self.goToLogin)
    def show(self):
        self.ui.show()
    def register(self):
        login = self.ui.input_login
        password = self.ui.input_password
        password_sec = self.ui.input_password_repeat
        if login.text() == '': login.setPlaceholderText("Введите логин!")
        if password.text() != password_sec.text():password_sec.setText(''); password_sec.setPlaceholderText("Пароли не совпадают!")
        elif password.text() == '': password.setPlaceholderText("Введите пароль!")
        else: print('Данные пользователя: ' + login.text() + ':' + password.text()); self.ui.close()

    def goToLogin(self):
        # Да, это импорт посередине кода. Если указать его сверху, то компилятор распознает его как зацикленный
        # Поэтому файл ипортируется только тогда, когда нужно
        from login_form import LoginForm

        self.ui.hide()
        self.ui = LoginForm()
        self.ui.show()
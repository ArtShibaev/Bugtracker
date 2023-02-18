from PySide6 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader

loader = QUiLoader()

class LoginForm(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load('interface.ui', None)
        self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)
        self.ui.submit_button.clicked.connect(self.do_smth)
        self.ui.show_password.stateChanged.connect(self.show_hide_password)
    def show(self):
        self.ui.show()
    def do_smth(self):
        print(self.ui.input_login.text() + ':' + self.ui.input_password.text())
    def show_hide_password(self):
        if self.ui.show_password.isChecked(): self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Normal)
        else: self.ui.input_password.setEchoMode(self.ui.input_password.EchoMode.Password)
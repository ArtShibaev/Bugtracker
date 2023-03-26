import os
import sys
from PySide6 import QtWidgets
from login_form import LoginForm


os.environ['PYSIDE_DESIGNER_PLUGINS'] = '.'

app = QtWidgets.QApplication(sys.argv)

window = LoginForm()
window.show()




app.exec_()

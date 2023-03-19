import os
import sys
from PySide2 import QtWidgets
from login_form import LoginForm


os.environ['PYSIDE_DESIGNER_PLUGINS'] = '.'

app = QtWidgets.QApplication(sys.argv)

window = LoginForm()
window.show()




app.exec_()

from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader

from image_loader import Images

loader = QUiLoader()

class WelcomePageForm(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.ui = loader.load('./interfaces/welcome_page.ui', None)
        Images.load_image(self)

    def show(self):
        self.ui.show()
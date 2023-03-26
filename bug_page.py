import os

from PySide2 import QtCore
from PySide2.QtCore import Qt
from PySide2.QtUiTools import QUiLoader
from pymongo import MongoClient

from image_loader import Images

loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
projects = db['projects']

class BugPage(QtCore.QObject):
    def __init__(self, uid, login, project, bid):
        print('Переход на', bid)
        self.uid = uid
        self.login = login
        super().__init__()
        self.ui = loader.load('./interfaces/bug_page.ui', None)
        self.ui.verticalLayout_5.setAlignment(Qt.AlignLeft)

        Images.load_image(self, 'bug_page')
        self.ui.home.clicked.connect(self.goToMainPage)

        bugs = project['bugs']

        for x in bugs:
            if x['bid'] == bid:
                self.bug = x
                print(self.bug)
                break

        self.ui.title.setText(self.bug['title'])

    def show(self):
        self.ui.show()

    def goToMainPage(self):
        from main_page import MainPage

        self.ui.hide()
        self.ui = MainPage(self.uid, self.login)
        self.ui.show()
from PySide6 import QtCore, QtGui
from PySide6.QtUiTools import QUiLoader
from pymongo import MongoClient
from datetime import datetime

import os
from dotenv import load_dotenv

from bug_card import BugCard
from image_loader import Images

load_dotenv('.env')


loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']
projects = db['projects']



class MainPage(QtCore.QObject):
    def __init__(self, uid):
        super().__init__()
        self.ui = loader.load('./interfaces/main_page.ui', None)
        self.fillingProjectList(uid)
        certainProject = projects.find_one({'owner': uid})
        self.fillBugCards(certainProject)

        Images.load_image(self, 'main_page')

    def show(self):
        self.ui.show()

    def fillingProjectList(self, uid):
        res = list(projects.find({'owner': uid}))
        for project in res:
            self.ui.projects_list.addItem(project["title"])

    def fillBugCards(self, project):
        for bug in project['bugs']:
            bug = BugCard(bug['title'], datetime.utcfromtimestamp(bug['createdDate']/1000).strftime('%d.%m.%Y %H:%M'), bug['author'], bug['assignee'], bug['tags'], bug['criticality'])
            self.ui.bug_cards.addWidget(bug)


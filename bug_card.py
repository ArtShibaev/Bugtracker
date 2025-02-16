import os
import random
import re

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget, QLabel
from pymongo import MongoClient

loader = QUiLoader()
mongo_url = os.environ.get('MONGO_URL')
client = MongoClient(mongo_url)
db = client['bugtracker']
users = db['users']


def findUser(uid):
    user = users.find_one({'uid': uid})
    return user

class BugCard(QWidget):
    def __init__(self, title, date, author_id, assignee_id, tags, criticality, styles):
        super().__init__()

        # Set up the widget's layout
        file = loader.load('./interfaces/bug_card.ui')
        layout = file.layout()
        self.setLayout(layout)
        file.frame_4.setStyleSheet(styles[0])
        for x in self.findChildren(QLabel):
            x.setStyleSheet(styles[1])
        file.title.setText(title)
        file.date.setText(date)
        file.author.setText(findUser(author_id)['login'])
        if assignee_id != 'Нет':
            file.assignee.setText(findUser(assignee_id)['login'])
        else:
            file.assignee.setText('Нет')

        if criticality == 'high':
            file.criticality.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(251, 61, 61, 255), stop:1 rgba(152, 38, 38, 255));border-radius: 14px;')
        elif criticality == 'medium':
            file.criticality.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255, 149, 26, 255), stop:1 rgba(255, 187, 13, 255));border-radius: 14px;')
        elif criticality == 'low':
            file.criticality.setStyleSheet('background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(16, 148, 53, 255), stop:1 rgba(29, 215, 81, 255));border-radius: 14px;')

        tags_string = ', '.join([tag for tag in tags])

        file.tags.setText(tags_string)

        self.setFixedSize(240, 160)

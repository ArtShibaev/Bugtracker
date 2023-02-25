from PySide6 import QtCore, QtGui
import os

class Images(QtCore.QObject):

    def load_image(self, file):
        if file == 'welcome_page':
            self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
            self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
            self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
            self.ui.sp_new_project.setIcon(QtGui.QIcon('./images/plus.png'))
            self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))
        elif file == 'main_page':
            self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
            self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
            self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
            self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))
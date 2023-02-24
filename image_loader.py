from PySide6 import QtCore, QtGui

class Images(QtCore.QObject):

    def load_image_for_welcome_page(self):
        self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
        self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
        self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
        self.ui.sp_new_project.setIcon(QtGui.QIcon('./images/plus.png'))
        self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))

    def load_image_for_main_page(self):
        self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
        self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
        self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
        self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))
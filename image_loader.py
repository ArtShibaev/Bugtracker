from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QColor


class Images(QtCore.QObject):

    def load_image(self, file):
        if file == 'welcome_page':
            self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
            self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
            self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
            self.ui.sp_new_project.setIcon(QtGui.QIcon('./images/plus.png'))
            self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))

        elif file == 'main_page':
            home = QPixmap('./images/main_page.png')
            # Исходное изображение черное. Создается маска для всего черного цвета на картинке
            mask = home.createMaskFromColor(QColor('#80828A'), Qt.MaskOutColor)
            # Маска закрашивается нужным цветом
            home.fill((QColor('#fff')))
            home.setMask(mask)

            self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
            self.ui.home.setIcon(QtGui.QIcon(home))
            self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
            self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))

            self.ui.change.setIcon(QtGui.QIcon('./images/gear.png'))
        elif file == 'bug_page':
            self.ui.new_project.setIcon(QtGui.QIcon('./images/plus.png'))
            self.ui.send.setIcon(QtGui.QIcon('./images/send_message.png'))
            self.ui.send.setIconSize(QSize(120, 120))
            self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
            self.ui.settings.setIcon(QtGui.QIcon('./images/gear.png'))
            self.ui.users_photo.setIcon(QtGui.QIcon('./images/user_icon.png'))

        elif file == 'settings_page' or file == 'settings_notifications_page':
            settings = QPixmap('./images/gear.png')
            mask = settings.createMaskFromColor(QColor('#80828A'), Qt.MaskOutColor)
            settings.fill((QColor('#fff')))
            settings.setMask(mask)

            self.ui.home.setIcon(QtGui.QIcon('./images/main_page.png'))
            self.ui.settings.setIcon(QtGui.QIcon(settings))
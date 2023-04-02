from desktop_notifier import DesktopNotifier, Urgency

notifier = DesktopNotifier()
DesktopNotifier.app_name = 'Багтрекер'


def sendError(title='Ошибка', message='Неизвестная ошибка'):
    notifier.send_sync(title=title, message=message)

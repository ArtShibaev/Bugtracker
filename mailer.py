from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib



def sendMail(to, subject, message):
    msg = MIMEMultipart()

    # Пароль приложения, который нужен для аутентификаци по SMTP
    password = "emxyavfaftjmqpym"
    msg['From'] = "bugtrackermailing@gmail.com"
    # log:pass bugtrackermailing@gmail.com:12345Qweasd
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'html'))

    server = smtplib.SMTP('smtp.gmail.com: 587')

    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("Отправлено %s" % (msg['To']))
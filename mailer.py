from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os


def sendMail(to, subject, message):
    msg = MIMEMultipart()

    # Пароль приложения, который нужен для аутентификаци по SMTP
    password = os.environ.get("MAIL_PASSWORD")
    msg["From"] = os.environ.get("MAIL_LOGIN")
    msg["To"] = to
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "html"))

    server = smtplib.SMTP("smtp.gmail.com: 587")

    server.starttls()
    server.login(msg["From"], password)
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    server.quit()
    print("Отправлено %s" % (msg["To"]))

import smtplib
import ssl
from email.message import EmailMessage
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def send_mail(to_email=(config["Mail server"]["receiver"],), subject=None, message=None,
              smtp=config["Mail server"]["smtp"], from_email=config["Mail server"]["email"],
              password=config["Mail server"]["password"]):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_email)
    msg.set_content(message)
    print(msg)
    context = ssl.create_default_context()
    server = smtplib.SMTP(smtp, 587)
    server.starttls(context=context)
    server.login(from_email, password)  # user & password
    server.sendmail(from_email, to_email, message)
    server.quit()
    print('successfully sent the mail.')
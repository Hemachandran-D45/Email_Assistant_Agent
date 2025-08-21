import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GmailSender:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password

    def send_email(self, to: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg["From"] = self.user
        msg["To"] = to
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, to, msg.as_string())

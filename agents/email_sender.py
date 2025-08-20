# agents/email_sender.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class EmailSenderAgent:
    def __init__(self):
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 465))  # SSL port

        if not self.user or not self.password:
            raise ValueError("❌ Missing SMTP_USER or SMTP_PASS in .env")

    def send_email(self, to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg["From"] = self.user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.user, self.password)
                server.sendmail(self.user, to_email, msg.as_string())
            print(f"✅ Email sent to {to_email}")
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            raise

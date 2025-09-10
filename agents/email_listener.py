import imaplib
import email
from email.header import decode_header
import time
from typing import Optional, Dict

class ZohoListener:
    def __init__(self, user: str, password: str):
        self.user = user
        self.password = password
        self.imap = None

    def connect(self):
        self.imap = imaplib.IMAP4_SSL("imap.zoho.com")
        self.imap.login(self.user, self.password)

    def wait_for_email(self, timeout: int = 60) -> Optional[Dict]:
        """Waits for a new unseen email for up to `timeout` seconds."""
        self.connect()
        self.imap.select("inbox")

        start = time.time()
        while time.time() - start < timeout:
            status, messages = self.imap.search(None, '(UNSEEN)')
            if status == "OK":
                ids = messages[0].split()
                if ids:
                    latest_id = ids[-1]
                    _, msg_data = self.imap.fetch(latest_id, "(RFC822)")
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")

                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors="ignore")
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors="ignore")

                    return {
                        "sender": msg["From"],
                        "subject": subject,
                        "body": body,
                    }
            time.sleep(5)
        return None

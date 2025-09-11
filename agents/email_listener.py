import imaplib
import email
from email.header import decode_header
import time
from typing import Optional, Dict
from email.utils import parseaddr


class ZohoListener:
    def __init__(self, user: str, password: str):
        self.user = user.strip() if user else None
        self.password = password.strip() if password else None
        self.imap = None

    def connect(self):
        print(f"📥 Connecting to Zoho IMAP as: {self.user}")  # Debug (email only, not password)
        if not self.user or not self.password:
            raise ValueError("❌ Missing Zoho email or password")
        
        # Explicit host + port
        self.imap = imaplib.IMAP4_SSL("imap.zoho.in", 993)
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

                    # Extract only the email address from "Name <email@domain.com>"
                    _, sender_email = parseaddr(msg["From"])

                    return {
                        "id": latest_id.decode() if isinstance(latest_id, bytes) else str(latest_id),
                        "sender": sender_email,
                        "subject": subject,
                        "body": body,
                    }
            time.sleep(5)
        return None

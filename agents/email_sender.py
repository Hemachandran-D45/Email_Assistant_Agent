import os
from mailslurp_client import Configuration, ApiClient, SendEmailOptions, InboxControllerApi, EmailControllerApi
from dotenv import load_dotenv

load_dotenv()

class EmailSenderAgent:
    def __init__(self):
        api_key = os.getenv("MAILSLURP_API_KEY")
        if not api_key:
            raise ValueError("❌ MAILSLURP_API_KEY is missing!")

        configuration = Configuration()
        configuration.api_key["x-api-key"] = api_key

        self.client = ApiClient(configuration)
        self.inbox_api = InboxControllerApi(self.client)
        self.email_api = EmailControllerApi(self.client)

        self.inbox_id = os.getenv("MAILSLURP_INBOX_ID")
        if not self.inbox_id:
            inbox = self.inbox_api.create_inbox()
            self.inbox_id = inbox.id
            print(f"📬 New inbox created: {self.inbox_id}")

    def send_email(self, to_email: str, subject: str, body: str):
        send_options = SendEmailOptions(to=[to_email], subject=subject, body=body)
        self.email_api.send_email(self.inbox_id, send_options)
        print(f"✅ Email sent to {to_email}")

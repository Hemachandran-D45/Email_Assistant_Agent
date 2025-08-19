import os
from mailslurp_client import Configuration, ApiClient, InboxControllerApi, WaitForControllerApi
from dotenv import load_dotenv

load_dotenv()

class EmailListenerAgent:
    def __init__(self):
        api_key = os.getenv("MAILSLURP_API_KEY")
        if not api_key:
            raise ValueError("❌ MAILSLURP_API_KEY is missing in .env file!")

        configuration = Configuration()
        configuration.api_key["x-api-key"] = api_key

        self.client = ApiClient(configuration)
        self.inbox_api = InboxControllerApi(self.client)
        self.wait_api = WaitForControllerApi(self.client)

        self.inbox_id = os.getenv("MAILSLURP_INBOX_ID")
        if not self.inbox_id:
            inbox = self.inbox_api.create_inbox()
            self.inbox_id = inbox.id
            print(f"📬 New inbox created: {self.inbox_id}")

    def wait_for_email(self, timeout=30):
        """Wait for the latest unread email (blocking)."""
        email = self.wait_api.wait_for_latest_email(
            inbox_id=self.inbox_id,
            timeout=timeout * 1000,
            unread_only=True
        )
        return {
            "id": email.id,
            "sender": email.from_,
            "subject": email.subject,
            "body": email.body
        }

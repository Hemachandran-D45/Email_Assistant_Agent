from agents.inbox_listener import EmailListenerAgent
from agents.thread_detector import ThreadDetector
from agents.classifier import ClassifierAgent
from agents.draft_generator import DraftGeneratorAgent
from agents.email_sender import EmailSenderAgent
from utils.logger import *
from utils.hil_queue import enqueue as hil_enqueue

def main():
    listener = EmailListenerAgent()
    detector = ThreadDetector()
    classifier = ClassifierAgent()
    drafter = DraftGeneratorAgent()
    sender = EmailSenderAgent()

    print("📬 Waiting for new emails...")

    while True:
        email = listener.wait_for_email(timeout=60)
        print(f"📩 New email received: {email}")

        thread_id = detector.detect_or_create_thread(email["sender"], email["body"])
        classification = classifier.classify(email["body"])

        log_classification(email_id=email["id"], thread_id=thread_id,
                           category=classification["category"],
                           tone=classification.get("tone","unknown"),
                           raw=classification)

        draft = drafter.generate_draft(email, thread_id)
        log_draft(email_id=email["id"], thread_id=thread_id,
                  reply=draft["reply"], confidence=draft["confidence"], history_hits=3)

        if draft["confidence"] >= 9:
            sender.send_email(email["sender"], f"Re: {email['subject']}", draft["reply"])
            log_send(email_id=email["id"], thread_id=thread_id,
                     to_email=email["sender"], subject=f"Re: {email['subject']}")
        else:
            hil_id = hil_enqueue(email=email, thread_id=thread_id, draft=draft)
            log_hil_queued(email_id=email["id"], thread_id=thread_id, confidence=draft["confidence"])
            print(f"👤 Queued for human review (id={hil_id}). Open the Streamlit app to review.")

if __name__ == "__main__":
    main()

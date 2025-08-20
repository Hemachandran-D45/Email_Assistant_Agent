# workflow.py
from langgraph.graph import StateGraph, END
from utils.types import State
from agents.email_listener import EmailListenerAgent
from agents.classifier import ClassifierAgent
from agents.draft_generator import DraftGeneratorAgent
from agents.email_sender import EmailSenderAgent
from utils.hil_queue import enqueue
from utils.logger import log_classification, log_draft, log_send, log_hil_queued

CONFIDENCE_THRESHOLD = 9  # route to auto-send if >= 9

def build_workflow():
    sg = StateGraph(State)

    listener = EmailListenerAgent()
    classifier = ClassifierAgent()
    drafter = DraftGeneratorAgent()
    sender = EmailSenderAgent()

    def listen_node(state: State) -> State:
        email = listener.wait_for_email(timeout=60)
        return {"email": email}

    def classify_node(state: State) -> State:
        email = state["email"]
        classification = classifier.classify(email)
        # thread id is decided at draft stage (ThreadDetector)
        log_classification(email["id"], "?", classification["category"], classification.get("tone","neutral"), classification)
        return {"classification": classification}

    def draft_node(state: State) -> State:
        email = state["email"]
        draft = drafter.generate_reply(email, state["classification"])
        log_draft(email["id"], draft["thread_id"], draft["reply"], draft["confidence"], draft["history_hits"])
        return {"draft": draft, "thread_id": draft["thread_id"]}

    def decision_node(state: State) -> State:
        email, draft = state["email"], state["draft"]
        if draft["confidence"] >= CONFIDENCE_THRESHOLD:
            sender.send_email(
                to_email=email["sender"],
                subject=f"Re: {email['subject']}",
                body=draft["reply"]
            )
            log_send(email["id"], state["thread_id"], email["sender"], f"Re: {email['subject']}")
        else:
            enqueue(email, draft, state["thread_id"])
            log_hil_queued(email["id"], state["thread_id"], draft["confidence"])
        return {}

    sg.add_node("listen", listen_node)
    sg.add_node("classify", classify_node)
    sg.add_node("draft", draft_node)
    sg.add_node("decide", decision_node)

    sg.set_entry_point("listen")
    sg.add_edge("listen", "classify")
    sg.add_edge("classify", "draft")
    sg.add_edge("draft", "decide")
    sg.add_edge("decide", END)

    return sg.compile()

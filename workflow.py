import os
from dotenv import load_dotenv 
from IPython.display import display,Image
from langgraph.graph import StateGraph, END
from utils.types import State
from agents.email_listener import ZohoListener
from agents.classifier import ClassifierAgent
from agents.draft_generator import DraftGeneratorAgent
from agents.email_sender import ZohoSender
from utils.hil_queue import enqueue
from utils.logger import log_classification, log_draft, log_send, log_hil_queued

load_dotenv()  
CONFIDENCE_THRESHOLD = 9 
zoho_user = os.getenv("ZOHO_USER")
zoho_pass = os.getenv("ZOHO_PASS")


def build_workflow():
    
    sg = StateGraph(State)
    listener = ZohoListener(zoho_user, zoho_pass)
    sender = ZohoSender(zoho_user, zoho_pass)
    classifier = ClassifierAgent()
    drafter = DraftGeneratorAgent()


    def listen_node(state: State) -> State:
        email = listener.wait_for_email(timeout=60)
        if not email:
            print("⚠️ No new emails found within timeout.")
            return {"email": None}   # prevent crash
        return {"email": email}

    def classify_node(state: State) -> State:
        email = state["email"]
        if email is None:
            print("⚠️ No email to classify.")
            return {"classification": None}
        
        classification = classifier.classify(email)
        log_classification(
            email.get("id", "?"),
            "?",
            classification["category"],
            classification.get("tone", "neutral"),
            classification,
        )
        return {"classification": classification}


    def draft_node(state: State) -> State:
        email = state["email"]
        classification = state.get("classification")
        if email is None or classification is None:
            print("⚠️ No email or classification available for drafting.")
            return {"draft": None, "thread_id": None}

        draft = drafter.generate_reply(email, classification)
        log_draft(
            email.get("id", "?"),
            draft["thread_id"],
            draft["reply"],
            draft["confidence"],
            draft["history_hits"]
        )
        return {"draft": draft, "thread_id": draft["thread_id"]}

    def decision_node(state: State) -> State:
        email, draft = state["email"], state.get("draft")
        if email is None or draft is None:
            print("⚠️ Nothing to send or enqueue.")
            return {}

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

if __name__ == "__main__":
    graph_builder = build_workflow()
    try:
        from IPython.display import display, Image
        display(Image(graph_builder.get_graph().draw_mermaid_png()))
    except Exception:
        print("Diagram rendering skipped (not in notebook).")



# graph_builder = build_workflow()
# with open("workflow_graph.png", "wb") as f:
#     f.write(graph_builder.get_graph().draw_mermaid_png())
# print("✅ Workflow diagram saved as workflow_graph.png")


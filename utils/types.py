from typing import TypedDict

class Email(TypedDict):
    id: str
    sender: str
    subject: str
    body: str

class Classification(TypedDict):
    category: str         # spam | urgent | quick_reply | normal
    tone: str             # neutral | angry | happy | frustrated | formal | informal
    confidence: float     # confidence score from classifier

class Draft(TypedDict):
    reply: str
    confidence: float     # 1-10, used for routing
    history_hits: int
    thread_id: str

class State(TypedDict, total=False):
    email: Email
    classification: Classification
    draft: Draft
    thread_id: str

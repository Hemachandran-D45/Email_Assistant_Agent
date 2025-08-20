# utils/chroma_db.py
import os
from typing import List, Optional, Dict, Any
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

PERSIST_DIR = os.path.join(os.getcwd(), "vectorstore", "index")

_vectorstore: Optional[Chroma] = None
_embeddings: Optional[HuggingFaceEmbeddings] = None

def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return _embeddings

def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        os.makedirs(PERSIST_DIR, exist_ok=True)
        _vectorstore = Chroma(
            collection_name="emails",
            persist_directory=PERSIST_DIR,
            embedding_function=_get_embeddings(),
        )
    return _vectorstore

def add_email_to_index(email: dict, thread_id: str):
    vs = get_vectorstore()
    text = f"From: {email['sender']}\nSubject: {email['subject']}\n\n{email['body']}"
    doc = Document(
        page_content=text,
        metadata={"email_id": email["id"], "sender": email["sender"], "thread_id": thread_id},
    )
    vs.add_documents([doc])

def similarity_search(query: str, k: int = 3, _filter: Optional[Dict[str, Any]] = None) -> List[Document]:
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k, filter=_filter) if _filter else vs.similarity_search(query, k=k)

def similarity_search_with_score(query: str, k: int = 1):
    vs = get_vectorstore()
    return vs.similarity_search_with_score(query, k=k)

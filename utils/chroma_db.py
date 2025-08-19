import chromadb

def get_chroma_client():
    return chromadb.PersistentClient(path="./chroma_db")

def get_email_collection():
    client = get_chroma_client()
    try:
        return client.get_collection("email_history")
    except:
        return client.create_collection("email_history")

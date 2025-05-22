from pymongo import MongoClient
from uuid import uuid4
from datetime import datetime
from db import SessionLocal, init_db
from connection_postgres import embeddings
from embeddings_question import get_embedding
from dotenv import load_dotenv
from tqdm import tqdm
import os

load_dotenv()

clientmongo = os.getenv("CLIENTMONGO")
database = os.getenv("DATABASE")
collectiondb = os.getenv("COLLECTIONDB")

# Connexion MongoDB
client = MongoClient(clientmongo)
db_mongo = client[database]
collection = db_mongo[collectiondb]

def clean_string(value):
    """Supprime les caractères nuls (0x00) des chaînes de caractères."""
    if isinstance(value, str):
        return value.replace('\x00', '')
    return value

def process_message(session, message, title, course_id, username, created_at, suffix=""):
    text = clean_string(message.get("body", ""))
    if not text:
        return 0

    try:
        embedding = get_embedding(text)
        chunk = embeddings(
            id=uuid4(),
            text=text,
            title=clean_string(title + suffix),
            course_id=clean_string(course_id),
            username=clean_string(message.get("username", username)),
            created_at=created_at,
            embedding=embedding
        )
        session.add(chunk)
        session.commit()
        return 1
    except Exception as e:
        session.rollback()
        print(f"[⚠️ ERREUR INSERTION] : {e}")
        return 0

def extract_and_insert():
    init_db()
    session = SessionLocal()

    # Récupère les messages non encore indexés
    docs = list(collection.find({"indexed": {"$ne": True}}))

    # Calcul du nombre total de messages
    total_messages = sum(
        1 + len(doc.get("content", {}).get("children", [])) for doc in docs
    )

    total_inserted = 0

    with tqdm(total=total_messages, desc="Indexation des messages") as pbar:
        for doc in docs:
            content = doc.get("content", {})
            title = content.get("courseware_title", "")
            course_id = content.get("course_id", "")
            username = content.get("username", "") or doc.get("username", "")
            created_at_raw = content.get("created_at") or doc.get("created_at")

            try:
                created_at = datetime.fromisoformat(
                    created_at_raw.replace("Z", "+00:00")
                ) if created_at_raw else datetime.utcnow()
            except Exception:
                created_at = datetime.utcnow()

            total_inserted += process_message(session, content, title, course_id, username, created_at)
            pbar.update(1)

            children = content.get("children", [])
            if isinstance(children, list):
                for i, child in enumerate(children, start=1):
                    suffix = f" - Réponse {i}"
                    total_inserted += process_message(session, child, title, course_id, username, created_at, suffix)
                    pbar.update(1)

            # Marque le document comme indexé pour ne pas le retraiter
            collection.update_one({"_id": doc["_id"]}, {"$set": {"indexed": True}})

    session.close()
    print(f"\n✅ Indexation terminée : {total_inserted} lignes insérées.")

if __name__ == "__main__":
    extract_and_insert()

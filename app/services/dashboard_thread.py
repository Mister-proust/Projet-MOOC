from pymongo import MongoClient
from services.sentiment_analysis import analyze_sentiment
from langdetect import detect

client = MongoClient("mongodb://localhost:27017/")
collection = client["MOOC"]["forum"]

def get_thread_with_messages(thread_id):
    """
    Récupère tous les messages du thread (body du thread + children).
    Analyse les sentiments.
    """
    doc = collection.find_one({"content.id": thread_id})
    if not doc:
        return []

    messages = []

    # Message principal
    thread = doc["content"]
    messages.append({
        "text": thread["body"],
        "username": thread["username"]
    })

    # Réponses
    for child in thread.get("children", []):
        messages.append({
            "text": child["body"],
            "username": child["username"]
        })

    # Analyse de sentiment
    texts = [msg["text"] for msg in messages]
    sentiments = analyze_sentiment(texts)

    for msg, sent in zip(messages, sentiments):
        msg["sentiment"] = sent["label"]
        msg["score"] = round(sent["score"] * 100, 1)  # % pour l'affichage
        msg["language"] = detect(msg["text"])

    return messages

def get_all_courses():
    """
    Récupère tous les course_id distincts dans la base.
    """
    return collection.distinct("content.course_id")

def get_threads_for_course(course_id):
    """
    Récupère tous les threads (id et titre) pour un cours donné.
    """
    threads = collection.find({
        "content.course_id": course_id,
        "content.type": "thread"
    }, {"content.id": 1, "content.title": 1}).limit(100)

    return [{"id": t["content"]["id"], "title": t["content"].get("title", "")} for t in threads]

from sqlalchemy import text
from services.db import SessionLocal
from services.embeddings_question import get_embedding

def search_similar_message(query_text):
    session = SessionLocal()
    query_embedding = get_embedding(query_text)

    sql = text("""
    SELECT id, text, title, course_id, username, created_at, embedding <=> CAST(:embedding AS vector) AS distance
    FROM public.embeddings_pgvector
    ORDER BY distance ASC
    LIMIT 1
    """)

    result = session.execute(sql, {"embedding": query_embedding}).fetchone()
    session.close()

    if result:
        return {
            "id": result.id,
            "text": result.text,
            "title": result.title,
            "course_id": result.course_id,
            "username": result.username,
            "created_at": result.created_at,
            "distance": result.distance
        }
    else:
        return None


def get_thread_messages(title, course_id):
    """Récupère tous les messages d'un fil de discussion basé sur le titre et course_id"""
    session = SessionLocal()
    
    sql = text("""
    SELECT id, text, title, course_id, username, created_at
    FROM public.embeddings_pgvector
    WHERE title = :title AND course_id = :course_id
    ORDER BY created_at ASC
    """)
    
    results = session.execute(sql, {"title": title, "course_id": course_id}).fetchall()
    session.close()
    
    if results:
        return [
            {
                "id": result.id,
                "text": result.text,
                "title": result.title,
                "course_id": result.course_id,
                "username": result.username,
                "created_at": result.created_at
            }
            for result in results
        ]
    else:
        return []
from pymongo import MongoClient
from collections import defaultdict

client = MongoClient('mongodb://localhost:27017/')
db = client['MOOC']
collection = db['forum']


def jaccard(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0


def get_all_usernames():
    return collection.distinct("content.username")


def get_similarity_scores(participant: str):
    usernames = get_all_usernames()
    usernames = [u for u in usernames if u != participant]

    threads = collection.find({ "content.username": participant })
    comments = collection.find({ "content.children.username": participant })

    cours_participant = set()
    threads_participant = set()

    for doc in threads:
        cours_participant.add(doc['content']['course_id'])
        threads_participant.add(doc['content']['id'])

    for doc in comments:
        cours_participant.add(doc['content']['course_id'])
        threads_participant.add(doc['content']['id'])

    user_cours = defaultdict(set)
    user_threads = defaultdict(set)

    docs = collection.find({ "content.username": {"$in": usernames} })
    for doc in docs:
        user = doc['content']['username']
        user_cours[user].add(doc['content']['course_id'])
        user_threads[user].add(doc['content']['id'])

    docs_comments = collection.find({ "content.children.username": {"$in": usernames} })
    for doc in docs_comments:
        children = doc['content'].get('children', [])
        for child in children:
            user = child['username']
            user_cours[user].add(doc['content']['course_id'])
            user_threads[user].add(doc['content']['id'])

    resultats = []
    for other in usernames:
        cours_other = user_cours[other]
        threads_other = user_threads[other]

        score_cours = jaccard(cours_participant, cours_other)
        score_threads = jaccard(threads_participant, threads_other)
        score_moyen = (score_cours + score_threads) / 2

        resultats.append({
            "username": other,
            "score_cours": round(score_cours, 2),
            "score_threads": round(score_threads, 2),
            "score_moyen": round(score_moyen, 2),
        })

    resultats = sorted(resultats, key=lambda x: x["score_moyen"], reverse=True)
    return resultats[:10]

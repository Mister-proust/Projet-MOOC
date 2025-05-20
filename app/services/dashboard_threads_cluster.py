import os
from bertopic import BERTopic
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "bertopic_original_model"))
csv_path = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "df_questions.csv"))

model = BERTopic.load(model_path)
df = pd.read_csv(csv_path)

# Fonction pour obtenir les clusters
def get_all_clusters():
    topics_info = model.get_topic_info()
    return topics_info.to_dict(orient="records")

# Fonction pour récupérer les messages d'un topic donné
def get_messages_by_topic(topic_id: int):
    topic_assignments = model.topics_
    df["topic_id"] = topic_assignments

    filtered_df = df[df["topic_id"] == topic_id]
    return filtered_df[["contenu_message", "titre_sujet"]].to_dict(orient="records")

# Fonction pour obtenir les mots-clés d’un topic
def get_topic_keywords(topic_id: int):
    topic = model.get_topic(topic_id)
    return [word for word, _ in topic]

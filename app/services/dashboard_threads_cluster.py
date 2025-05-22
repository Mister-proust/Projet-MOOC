import os
from bertopic import BERTopic
import pandas as pd
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#model_path = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "bertopic_original_model"))
model_path = "../data/bertopic_original_model"
csv_path = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "data", "df_questions.csv"))

model = BERTopic.load(model_path)
df = pd.read_csv(csv_path)

def get_all_clusters():
    topics_info = model.get_topic_info()
    return topics_info.to_dict(orient="records")

def get_messages_by_topic(topic_id: int):
    if "topic_id" not in df.columns:
        df["topic_id"] = model.topics_

    filtered_df = df[df["topic_id"] == topic_id]
    return filtered_df[["contenu_message", "titre_sujet"]].to_dict(orient="records")

def get_topic_keywords(topic_id: int):
    topic = model.get_topic(topic_id)
    return [word for word, _ in topic]

def get_bertopic_html():
    fig = model.visualize_topics()
    return fig.to_html(full_html=False)


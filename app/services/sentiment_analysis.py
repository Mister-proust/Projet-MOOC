from transformers import pipeline

# Charger le pipeline une seule fois (au démarrage du serveur)
pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")

def analyze_sentiment(texts):
    """
    Analyse les sentiments d'une liste de textes.
    Retourne une liste de dicts : [{label: POSITIVE, score: 0.98}, ...]
    """
    return pipe(texts, truncation=True)

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  

def get_embedding(text: str) -> list[float]:
    return model.encode(text).tolist()

MODEL_NAME = "all-MiniLM-L6-v2"
model = None


def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(MODEL_NAME)
    return model

def embed_text(texts):
    return get_model().encode(texts)

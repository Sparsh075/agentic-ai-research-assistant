_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_texts(texts: list):
    model = _get_model()
    return model.encode(texts, show_progress_bar=True)

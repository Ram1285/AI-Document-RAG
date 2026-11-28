from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

_E5_QUERY_PREFIX = "query: "
_E5_PASSAGE_PREFIX = "passage: "


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model_name)


def embed_texts(texts: list[str], *, is_query: bool = False) -> np.ndarray:
    if not texts:
        return np.empty((0, 0), dtype="float32")

    model = get_embedding_model()
    model_name = get_settings().embedding_model_name.casefold()
    if model_name.startswith("intfloat/e5"):
        prefix = _E5_QUERY_PREFIX if is_query else _E5_PASSAGE_PREFIX
        texts = [f"{prefix}{text}" for text in texts]
    vectors = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return vectors.astype("float32")

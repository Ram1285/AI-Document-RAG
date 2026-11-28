import json
from pathlib import Path

import faiss
import numpy as np


class FaissVectorStore:
    def __init__(self, store_dir: Path):
        self.store_dir = store_dir
        self.index_path = self.store_dir / "index.faiss"
        self.metadata_path = self.store_dir / "metadata.json"
        self.index: faiss.Index | None = None
        self.metadata: list[dict] = []
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self._load()

    @property
    def size(self) -> int:
        return self.index.ntotal if self.index is not None else 0

    def add(self, vectors: np.ndarray, metadata: list[dict]) -> None:
        if vectors.size == 0:
            return

        if self.index is None:
            self.index = faiss.IndexFlatIP(vectors.shape[1])

        self.index.add(vectors)
        self.metadata.extend(metadata)
        self.save()

    def search(self, query_vector: np.ndarray, top_k: int, document_id: str | None = None) -> list[dict]:
        if self.index is None or self.index.ntotal == 0:
            return []

        search_k = min(max(top_k * 5, top_k), self.index.ntotal)
        scores, indexes = self.index.search(query_vector, search_k)

        results = []
        for score, index in zip(scores[0], indexes[0]):
            if index < 0:
                continue
            item = dict(self.metadata[index])
            if document_id and item["document_id"] != document_id:
                continue
            item["score"] = float(score)
            results.append(item)
            if len(results) == top_k:
                break

        return results

    def save(self) -> None:
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        self.metadata_path.write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        if self.metadata_path.exists():
            self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

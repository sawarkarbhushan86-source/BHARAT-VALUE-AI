"""Modular Embedding Generation Service with Fallback Support."""
import re
import math
from typing import List
from bharat_value_ai.config import settings

class EmbeddingService:
    """
    Generates dense embeddings for financial text chunks and queries.
    Uses Google GenAI embeddings if GEMINI_API_KEY is configured,
    or a fast, deterministic, high-dimensional TF-IDF / Subword Cosine Space.
    """

    DIMENSION = 384

    def __init__(self):
        self.api_key = settings.gemini_api_key

    def get_embedding(self, text: str) -> List[float]:
        """Generate a normalized 384-dimensional vector."""
        if self.api_key and len(self.api_key) > 10:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                response = client.models.embed_content(
                    model="text-embedding-004",
                    contents=text[:2000]
                )
                vec = response.embedding.values
                if len(vec) == self.DIMENSION:
                    return vec
                # Truncate or pad to self.DIMENSION if model output differs
                if len(vec) > self.DIMENSION:
                    return vec[:self.DIMENSION]
                return vec + [0.0] * (self.DIMENSION - len(vec))
            except Exception:
                pass

        return self._deterministic_dense_vector(text)

    def _deterministic_dense_vector(self, text: str) -> List[float]:
        """Fast, robust, 100% deterministic hash-projection embedding across Python processes."""
        import hashlib
        vector = [0.0] * self.DIMENSION
        tokens = re.findall(r"\b\w+\b", text.lower())
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            h = int.from_bytes(digest[:4], "big")
            idx = h % self.DIMENSION
            sign = 1.0 if (h >> 3) & 1 else -1.0
            vector[idx] += sign

        # L2 Normalize
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

embedding_service = EmbeddingService()

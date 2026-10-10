"""Isolated Vector Store Abstraction with Local SQLite / Memory Persistence."""
import json
import sqlite3
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from bharat_value_ai.config import settings
from bharat_value_ai.rag.embeddings import embedding_service

class VectorStore:
    """
    Lightweight, high-performance vector store with metadata filtering.
    Stores chunks, embeddings, and rich provenance metadata in SQLite.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(settings.vector_store_path) / "vector_index.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_vectors (
                    id TEXT PRIMARY KEY,
                    symbol TEXT,
                    document_title TEXT,
                    reporting_period TEXT,
                    publication_date TEXT,
                    section_title TEXT,
                    content TEXT,
                    source_url TEXT,
                    embedding_json TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_vec_symbol ON document_vectors(symbol)")
            conn.commit()

    def add_document_chunk(
        self,
        chunk_id: str,
        symbol: str,
        document_title: str,
        reporting_period: str,
        publication_date: str,
        section_title: str,
        content: str,
        source_url: str = ""
    ):
        embedding = embedding_service.get_embedding(content)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO document_vectors 
                (id, symbol, document_title, reporting_period, publication_date, section_title, content, source_url, embedding_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chunk_id, symbol.upper(), document_title, reporting_period,
                publication_date, section_title, content, source_url, json.dumps(embedding)
            ))
            conn.commit()

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def search(
        self,
        query: str,
        symbol: Optional[str] = None,
        date_cutoff: Optional[str] = None,
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant document chunks with cosine similarity ranking
        and metadata filtering (symbol and date cutoff).
        """
        query_vec = embedding_service.get_embedding(query)

        query_sql = "SELECT id, symbol, document_title, reporting_period, publication_date, section_title, content, source_url, embedding_json FROM document_vectors"
        params = []
        if symbol:
            query_sql += " WHERE symbol = ?"
            params.append(symbol.upper().replace(".NS", ""))

        candidates = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query_sql, params)
            rows = cursor.fetchall()

            for row in rows:
                c_id, c_sym, c_title, c_period, c_pub_date, c_sec, c_text, c_url, c_emb_json = row
                
                # Point-in-time date filtering
                if date_cutoff and c_pub_date and c_pub_date > date_cutoff:
                    continue

                emb = json.loads(c_emb_json)
                sim = self._cosine_similarity(query_vec, emb)
                candidates.append({
                    "chunk_id": c_id,
                    "symbol": c_sym,
                    "document_title": c_title,
                    "reporting_period": c_period,
                    "publication_date": c_pub_date,
                    "section_title": c_sec,
                    "content": c_text,
                    "source_url": c_url,
                    "similarity": round(sim, 4)
                })

        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        return candidates[:top_k]

    def count_indexed_chunks(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM document_vectors")
            return cur.fetchone()[0]

vector_store = VectorStore()

"""News Event Deduplication and Syndicate Clustering."""
import hashlib
import re
from typing import List, Dict, Any, Set

class NewsDeduplicator:
    """
    Identifies syndicated copies of the same news event across multiple publishers.
    Prevents artificial inflation of sentiment from wire services or repeated press releases.
    """

    @staticmethod
    def _get_shingles(text: str, k: int = 2) -> Set[str]:
        cleaned = re.sub(r"(\d+),(\d+)", r"\1\2", text.lower())
        words = re.findall(r"\b[a-zA-Z0-9]+\b", cleaned)
        shingles = set(w for w in words if len(w) > 1)
        for i in range(len(words) - 1):
            shingles.add(f"{words[i]} {words[i+1]}")
        return shingles

    @staticmethod
    def jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / union if union > 0 else 0.0

    def cluster_articles(self, articles: List[Dict[str, Any]], similarity_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """Group similar articles into duplicate clusters and tag novelty."""
        clusters: List[List[Dict[str, Any]]] = []

        for art in articles:
            title_text = f"{art.get('title', '')} {art.get('summary', '')}"
            art_shingles = self._get_shingles(title_text)
            art["shingles"] = art_shingles

            matched_cluster = None
            for cl in clusters:
                # Compare with the lead article of each cluster
                rep_shingles = cl[0]["shingles"]
                sim = self.jaccard_similarity(art_shingles, rep_shingles)
                if sim >= similarity_threshold:
                    matched_cluster = cl
                    break

            if matched_cluster is not None:
                matched_cluster.append(art)
            else:
                clusters.append([art])

        # Assign cluster IDs and mark original vs syndicated duplicate
        processed = []
        for i, cl in enumerate(clusters):
            cluster_id = f"cluster_{i+1:04d}"
            for idx, art in enumerate(cl):
                art_copy = {k: v for k, v in art.items() if k != "shingles"}
                art_copy["duplicate_cluster_id"] = cluster_id
                art_copy["is_original_story"] = (idx == 0)
                art_copy["cluster_story_count"] = len(cl)
                processed.append(art_copy)

        return processed

news_deduplicator = NewsDeduplicator()

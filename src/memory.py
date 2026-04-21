"""
最小可用 Memory 存储
使用本地 JSON 缓存 query、plan 和搜索结果。
"""

import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional


class MemoryStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.filepath = os.path.join(self.base_dir, "memory_store.json")

    def _empty_store(self) -> Dict[str, Any]:
        return {
            "records": []
        }

    def load_store(self) -> Dict[str, Any]:
        if not os.path.exists(self.filepath):
            return self._empty_store()

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._empty_store()

    def save_store(self, store: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)

    def normalize_text(self, text: str) -> str:
        return " ".join(text.lower().strip().split())

    def similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, self.normalize_text(a), self.normalize_text(b)).ratio()

    def find_similar_query(self, query: str, threshold: float = 0.85) -> Optional[Dict[str, Any]]:
        store = self.load_store()
        best_record = None
        best_score = 0.0

        for record in store["records"]:
            score = self.similarity(query, record.get("query_normalized", record.get("query", "")))
            if score > best_score:
                best_score = score
                best_record = record

        if best_record and best_score >= threshold:
            return best_record
        return None

    def find_search_cache(self, search_query: str, threshold: float = 0.92) -> Optional[List[Dict[str, Any]]]:
        store = self.load_store()
        best_results = None
        best_score = 0.0

        for record in store["records"]:
            for cache in record.get("search_cache", []):
                score = self.similarity(search_query, cache.get("search_query", ""))
                if score > best_score:
                    best_score = score
                    best_results = cache.get("results", [])

        if best_results is not None and best_score >= threshold:
            return best_results
        return None

    def upsert_record(
        self,
        query: str,
        plan: Dict[str, Any],
        search_cache: List[Dict[str, Any]],
        final_report_summary: Dict[str, Any]
    ) -> None:
        store = self.load_store()
        normalized_query = self.normalize_text(query)

        for record in store["records"]:
            if record.get("query_normalized") == normalized_query:
                record["plan"] = plan
                record["search_cache"] = search_cache
                record["final_report_summary"] = final_report_summary
                record["updated_at"] = datetime.now().isoformat()
                self.save_store(store)
                return

        store["records"].append({
            "query": query,
            "query_normalized": normalized_query,
            "created_at": datetime.now().isoformat(),
            "plan": plan,
            "search_cache": search_cache,
            "final_report_summary": final_report_summary
        })
        self.save_store(store)

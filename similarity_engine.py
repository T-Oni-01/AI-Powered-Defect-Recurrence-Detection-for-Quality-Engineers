from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class RecurrenceSummary:
    recurring: bool
    matches: pd.DataFrame
    top_category: Optional[str]
    top_sub_category: Optional[str]


class DefectSimilarityEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings: Optional[np.ndarray] = None
        self.data: Optional[pd.DataFrame] = None
        self.model_name = model_name

    def build_embeddings_with_cache(self, df, csv_path: str):
        """
        Load embeddings from cache if valid; otherwise build and save.
        """
        import numpy as np
        from core.cache import load_cache, save_cache, cache_is_valid

        # Try load cache
        cached, info = load_cache(csv_path, self.model_name)
        if cached is not None and info is not None and cache_is_valid(csv_path, self.model_name, info, len(df)):
            self.data = df.reset_index(drop=True)
            self.embeddings = cached
            return "cache"

        # Build fresh
        self.build_embeddings(df)
        save_cache(csv_path, self.model_name, self.embeddings, len(df))
        return "rebuilt"

    def save_cache_now(self, csv_path: str):
        """
        Save current embeddings to cache (call after appending record).
        """
        from core.cache import save_cache
        if self.data is None or self.embeddings is None:
            return
        save_cache(csv_path, self.model_name, self.embeddings, len(self.data))

    def build_embeddings(self, df: pd.DataFrame) -> None:
        if "description" not in df.columns:
            raise ValueError("Expected a 'description' column in dataframe.")
        self.data = df.reset_index(drop=True)
        self.embeddings = self.model.encode(self.data["description"].tolist())

    def build_embeddings_with_cache(self, df, csv_path: str):
        """
        Load embeddings from cache if valid; otherwise build and save.
        """
        import numpy as np
        from core.cache import load_cache, save_cache, cache_is_valid

        print(f"\n{'=' * 50}")
        print(f"Building embeddings for: {csv_path}")
        print(f"Current DataFrame has {len(df)} rows")

        # Try load cache
        cached, info = load_cache(csv_path, self.model_name)

        if cached is not None and info is not None:
            print(f"Found cache with {info.row_count} rows (model: {info.model_name})")
            print(f"Cache file stats - mtime: {info.csv_mtime}, size: {info.csv_size}, hash: {info.csv_hash}")

            # Validate cache
            if cache_is_valid(csv_path, self.model_name, info, len(df)):
                print("✓ Cache is valid, using cached embeddings")
                self.data = df.reset_index(drop=True)
                self.embeddings = cached
                return "cache"
            else:
                print("✗ Cache is invalid, rebuilding...")
        else:
            print("No valid cache found, building fresh embeddings...")

        # Build fresh
        print(f"Building fresh embeddings for {len(df)} descriptions...")
        self.build_embeddings(df)
        print(f"Saving cache with {len(df)} rows...")
        save_cache(csv_path, self.model_name, self.embeddings, len(df))
        print(f"✓ Saved new cache")
        print('=' * 50)
        return "rebuilt"

    def analyze_defect(
            self,
            new_description: str,
            section: Optional[str] = None,
            threshold: float = 0.75,
            top_k: int = 25,
    ) -> RecurrenceSummary:
        if self.data is None or self.embeddings is None:
            raise ValueError("Embeddings not built. Call build_embeddings(df) first.")

        print(f"Analyzing defect with {len(self.data)} records in memory")

        new_description = (new_description or "").strip()
        if not new_description:
            return RecurrenceSummary(False, pd.DataFrame(), None, None)

        new_embedding = self.model.encode([new_description])
        scores = cosine_similarity(new_embedding, self.embeddings)[0]

        # Optional section filter
        if section is not None:
            section = str(section).strip()
            mask = (self.data["section"].astype(str) == section).to_numpy()
            scores = scores * mask  # zero out non-matching sections

        # Get top candidates first for speed/cleaner output
        top_idx = np.argsort(scores)[::-1][:top_k]
        top_scores = scores[top_idx]

        # Keep only those above threshold
        keep = top_scores >= threshold
        kept_idx = top_idx[keep]

        print(f"Found {len(kept_idx)} matches above threshold")

        if kept_idx.size == 0:
            return RecurrenceSummary(False, pd.DataFrame(), None, None)

        matches = self.data.iloc[kept_idx].copy()
        matches["similarity_score"] = scores[kept_idx]
        matches = matches.sort_values("similarity_score", ascending=False)

        # Summaries
        top_category = None
        top_sub_category = None

        if "category" in matches.columns and matches["category"].notna().any():
            top_category = matches["category"].value_counts().index[0]

        if "sub_category" in matches.columns and matches["sub_category"].notna().any():
            top_sub_category = matches["sub_category"].value_counts().index[0]

        return RecurrenceSummary(True, matches, top_category, top_sub_category)

    def top_matches(self, new_description: str, section: str | None = None, top_k: int = 25):
        import pandas as pd
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity

        if self.data is None or self.embeddings is None:
            raise ValueError("Embeddings not built. Call build_embeddings(df) first.")

        new_description = (new_description or "").strip()
        if not new_description:
            return pd.DataFrame()

        new_embedding = self.model.encode([new_description])
        scores = cosine_similarity(new_embedding, self.embeddings)[0]

        if section is not None:
            section = str(section).strip()
            mask = (self.data["section"].astype(str) == section).to_numpy()
            scores = scores * mask

        top_idx = np.argsort(scores)[::-1][:top_k]
        matches = self.data.iloc[top_idx].copy()
        matches["similarity_score"] = scores[top_idx]
        return matches.sort_values("similarity_score", ascending=False)

    def likely_resolution(self, matches_df, not_recorded_value="Not Recorded"):
        """
        Returns (top_resolution, percent) or (None, None) if nothing usable.
        Only considers resolutions that are not empty and not 'Not Recorded'.
        """
        import pandas as pd

        if matches_df is None or matches_df.empty:
            return None, None

        if "resolution" not in matches_df.columns:
            return None, None

        s = matches_df["resolution"].dropna().astype(str).str.strip()
        s = s[(s != "") & (s.str.lower() != not_recorded_value.lower())]

        if s.empty:
            return None, None

        counts = s.value_counts()
        top = counts.index[0]
        pct = round(counts.iloc[0] / counts.sum() * 100, 2)
        return top, pct

    def add_record(self, record: dict) -> None:
        """
        Incrementally add a single record to the in-memory dataframe + embeddings.
        record must contain at least 'description'.
        """
        import pandas as pd
        import numpy as np

        if self.data is None or self.embeddings is None:
            raise ValueError("Embeddings not built. Load data + build embeddings first.")

        if "description" not in record or not str(record["description"]).strip():
            raise ValueError("Record must include a non-empty 'description'.")

        # Create 1-row df aligned to existing columns
        row_df = pd.DataFrame([record])

        # Ensure all columns exist
        for col in self.data.columns:
            if col not in row_df.columns:
                row_df[col] = ""

        # Reorder columns to match
        row_df = row_df[self.data.columns]

        # Append to data
        self.data = pd.concat([self.data, row_df], ignore_index=True)

        # Encode only the new description and append embedding
        new_emb = self.model.encode([str(record["description"])])
        self.embeddings = np.vstack([self.embeddings, new_emb])
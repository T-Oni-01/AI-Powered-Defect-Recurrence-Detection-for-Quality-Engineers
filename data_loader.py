import pandas as pd

class RepairDataLoader:
    def __init__(self):
        self.raw_df: pd.DataFrame | None = None

    def load_csv(self, file_path: str) -> pd.DataFrame:
        self.raw_df = pd.read_csv(file_path, encoding="latin1", low_memory=False)
        self.raw_df.columns = [c.strip().lower() for c in self.raw_df.columns]
        return self.raw_df

    def get_clean_view(self) -> pd.DataFrame:
        if self.raw_df is None:
            raise ValueError("No data loaded. Call load_csv() first.")

        base_required = ["jc_number", "description", "section", "date", "category", "sub_category"]
        missing = [c for c in base_required if c not in self.raw_df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # resolution is optional, but if it exists, include it
        cols = base_required + (["resolution"] if "resolution" in self.raw_df.columns else [])
        df = self.raw_df[cols].copy()

        df = df.dropna(subset=["jc_number", "description", "section", "date"])
        df["description"] = df["description"].astype(str).str.strip()
        df["category"] = df["category"].astype(str).str.strip()
        df["sub_category"] = df["sub_category"].astype(str).str.strip()
        df = df[df["description"] != ""]

        if "resolution" in df.columns:
            df["resolution"] = df["resolution"].astype(str).str.strip()

        df.reset_index(drop=True, inplace=True)
        return df
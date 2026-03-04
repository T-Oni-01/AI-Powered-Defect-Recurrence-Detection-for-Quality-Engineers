# core/data_cache.py
import os
import sys
import pickle
import hashlib
from typing import Optional
import pandas as pd

APP_NAME = "QE Defect AI"

def _user_cache_dir() -> str:
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(root, APP_NAME, "cache")
    os.makedirs(d, exist_ok=True)
    return d

def _cache_key(csv_path: str) -> str:
    p = os.path.abspath(csv_path)
    return hashlib.sha1(p.encode("utf-8")).hexdigest()[:16]

def _snapshot_path(csv_path: str) -> str:
    name = os.path.splitext(os.path.basename(csv_path))[0]
    key = _cache_key(csv_path)
    return os.path.join(_user_cache_dir(), f"{name}__{key}__df_snapshot.pkl")

def load_df_snapshot(csv_path: str) -> Optional[pd.DataFrame]:
    p = _snapshot_path(csv_path)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "rb") as f:
            df = pickle.load(f)
            return df
    except Exception as e:
        print(f"Error loading snapshot: {e}")
        return None

def save_df_snapshot(csv_path: str, df: pd.DataFrame) -> None:
    p = _snapshot_path(csv_path)
    # Ensure directory exists
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        pickle.dump(df, f, protocol=pickle.HIGHEST_PROTOCOL)
import json
import os, hashlib
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class CacheInfo:
    model_name: str
    csv_path: str
    csv_mtime: float
    csv_size: int
    row_count: int
    csv_hash: str = ""

APP_NAME = "QE Defect AI"

import hashlib

def file_sha256(path: str, max_bytes: int = 2_000_000) -> str:

    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(max_bytes))
    return h.hexdigest()

def _user_cache_dir() -> str:
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(root, APP_NAME, "cache")
    os.makedirs(d, exist_ok=True)
    return d

def _cache_paths(csv_path: str, model_name: str):
    safe_model = model_name.replace("/", "__")
    key = hashlib.sha1(os.path.abspath(csv_path).encode("utf-8")).hexdigest()[:16]
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    base = os.path.join(_user_cache_dir(), f"{base_name}__{key}")
    emb_path = f"{base}__embeddings__{safe_model}.npz"
    meta_path = f"{base}__embeddings__{safe_model}.json"
    return emb_path, meta_path


def load_cache(csv_path: str, model_name: str) -> tuple[Optional[np.ndarray], Optional[CacheInfo]]:
    emb_path, meta_path = _cache_paths(csv_path, model_name)
    if not (os.path.exists(emb_path) and os.path.exists(meta_path)):
        print(f"No cache files found at {emb_path} and {meta_path}")
        return None, None

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

            # FIX: Handle both tuple and string cases
            csv_hash_value = meta.get("csv_hash", "")
            if isinstance(csv_hash_value, tuple):
                csv_hash_value = csv_hash_value[0] if csv_hash_value else ""
            elif isinstance(csv_hash_value, list):
                csv_hash_value = csv_hash_value[0] if csv_hash_value else ""

        info = CacheInfo(
            model_name=meta["model_name"],
            csv_path=meta["csv_path"],
            csv_mtime=float(meta["csv_mtime"]),
            csv_size=int(meta["csv_size"]),
            row_count=int(meta["row_count"]),
            csv_hash=str(csv_hash_value),  # Ensure it's a string
        )

        arr = np.load(emb_path)["embeddings"]
        print(f"Loaded cache with {info.row_count} rows")
        return arr, info
    except Exception as e:
        print(f"Error loading cache: {e}")
        return None, None


def save_cache(csv_path: str, model_name: str, embeddings: np.ndarray, row_count: int) -> None:
    emb_path, meta_path = _cache_paths(csv_path, model_name)

    stat = os.stat(csv_path)
    meta = {
        "model_name": model_name,
        "csv_path": os.path.abspath(csv_path),
        "csv_mtime": float(stat.st_mtime),
        "csv_size": int(stat.st_size),
        "row_count": int(row_count),
        "csv_hash": file_sha256(csv_path),
    }

    np.savez_compressed(emb_path, embeddings=embeddings)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)


def cache_is_valid(csv_path: str, model_name: str, cache_info: CacheInfo, current_row_count: int) -> bool:
    """
    Validate if cache is still valid for the current CSV file.
    Returns False if cache should be rebuilt.
    """
    if cache_info.model_name != model_name:
        print(f"Cache invalid: model name mismatch")
        return False

    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Cache invalid: CSV file no longer exists")
        return False

    # Get current file stats
    try:
        stat = os.stat(csv_path)
    except Exception as e:
        print(f"Cache invalid: cannot stat CSV file: {e}")
        return False

    # ALWAYS check row count first - this should catch appends
    if current_row_count != cache_info.row_count:
        print(f"Cache invalid: row count changed from {cache_info.row_count} to {current_row_count}")
        return False

    # Check file size
    if stat.st_size != cache_info.csv_size:
        print(f"Cache invalid: file size changed from {cache_info.csv_size} to {stat.st_size}")
        return False

    # Check modification time (allow small floating point differences)
    if abs(stat.st_mtime - cache_info.csv_mtime) > 0.1:
        print(f"Cache invalid: modification time changed")
        return False

    # Only check hash if we have it and it's not empty
    if cache_info.csv_hash and cache_info.csv_hash != "None" and cache_info.csv_hash != "":
        try:
            current_hash = file_sha256(csv_path)
            if current_hash != cache_info.csv_hash:
                print(f"Cache invalid: file hash changed")
                return False
        except Exception as e:
            print(f"Warning: could not compute hash: {e}")
            # Don't invalidate just because hash failed

    print(f"Cache valid: using cached embeddings")
    return True
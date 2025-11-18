"""tools/sanitize_clients.py

Small helper to produce a sanitized/pseudonymized CSV from `data/clients.csv`.

It replaces `name`, `email`, `phone`, and `address` with deterministic
placeholders derived from the existing `id` so fixtures remain linkable but
PII is removed for safe sharing.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import pandas as pd
from typing import Optional


def _mask_value(value: str, prefix: str, id_seed: str) -> str:
    # deterministic short hash
    h = hashlib.sha256((id_seed + (value or "")).encode("utf-8")).hexdigest()[:8]
    return f"{prefix}_{h}"


def sanitize_clients(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    out = df.copy()
    for i, row in out.iterrows():
        seed = str(row.get("id") or i)
        out.at[i, "name"] = _mask_value(row.get("name", ""), "name", seed)
        out.at[i, "email"] = _mask_value(row.get("email", ""), "email", seed) + "@example.com"
        out.at[i, "phone"] = _mask_value(row.get("phone", ""), "phone", seed)
        out.at[i, "address"] = _mask_value(row.get("address", ""), "addr", seed)
        # keep non-PII fields like tags/status
    return out


def cli():
    p = argparse.ArgumentParser(description="Produce a sanitized clients CSV")
    p.add_argument("csv", nargs="?", default=os.path.join("data", "clients.csv"))
    p.add_argument("--out", help="Output path (defaults to stdout)")
    args = p.parse_args()
    df = sanitize_clients(args.csv)
    if args.out:
        df.to_csv(args.out, index=False)
    else:
        print(df.to_csv(index=False))


if __name__ == "__main__":
    cli()

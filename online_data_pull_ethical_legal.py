from dataclasses import dataclass
import csv
import json
import os
import re
import time
import uuid
from typing import Dict, Any, Optional
import pandas as pd
import requests

"""
online_data_pull_ethical_legal.py

Conservative, privacy-aware connectors for pulling publicly-available,
non-PII real-estate and product-related datasets.

Principles:
- Only fetch from public/open endpoints (user supplies URLs for many sources).
- Avoid collecting or persisting PII (addresses, emails, phone numbers).
- Sanitize and aggregate any potentially sensitive fields before saving.
- Respect remote service usage: set User-Agent, simple rate-limits.
- Run optional local security checks via overarching_security.py if present.

Usage:
- Import functions in your workflow or run this file as a script and edit
    the placeholders in main() to point to allowed public feeds/APIs.
"""



# Configuration
USER_AGENT = "MomWorkspaceDataPull/1.0 (+https://example.invalid) GitHub-Copilot"
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(BASE_DATA_DIR, exist_ok=True)


def _safe_request(url: str, params: dict = None, headers: dict = None, timeout: int = 20):
        headers = dict(headers or {})
        headers.setdefault("User-Agent", USER_AGENT)
        for attempt in range(3):
                try:
                        r = requests.get(url, params=params, headers=headers, timeout=timeout)
                        r.raise_for_status()
                        return r
                except requests.RequestException:
                        time.sleep(1 + attempt)
        raise RuntimeError(f"Failed to fetch {url} after retries")


def _backup_file(path: str):
        if os.path.exists(path):
                backup = f"{path}.bak.{uuid.uuid4().hex[:8]}"
                os.replace(path, backup)


# --- Sanitization helpers (conservative) ---
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
ADDRESS_KEYWORDS = {"address", "addr", "street", "city", "state", "zip", "postal"}


def sanitize_dataframe_remove_pii(df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove columns that likely contain PII based on column name or content heuristics.
        Mask strings that look like emails/phones.
        """
        df = df.copy()
        cols_to_drop = []
        for col in df.columns:
                low = col.lower()
                if any(k in low for k in ADDRESS_KEYWORDS) or "ssn" in low or "dob" in low:
                        cols_to_drop.append(col)
                        continue
                # If column values look like emails/phones, drop or mask
                sample = df[col].astype(str).head(10).str.cat(sep=" ")
                if EMAIL_RE.search(sample) or PHONE_RE.search(sample):
                        cols_to_drop.append(col)
        if cols_to_drop:
                df.drop(columns=cols_to_drop, inplace=True, errors="ignore")

        # Mask any remaining strings that contain emails or phones
        def _mask_value(v: Any):
                if not isinstance(v, str):
                        return v
                v = EMAIL_RE.sub("[REDACTED_EMAIL]", v)
                v = PHONE_RE.sub("[REDACTED_PHONE]", v)
                return v

        string_cols = df.select_dtypes(include=["object", "string"]).columns
        for c in string_cols:
                df[c] = df[c].map(_mask_value)

        return df


# --- Connector: download a publicly-published CSV (e.g., housing index) ---
def fetch_public_csv_to_dataframe(url: str) -> pd.DataFrame:
        """
        Download a public CSV and return a pandas DataFrame.
        Caller must ensure URL is a permitted public resource.
        """
        r = _safe_request(url)
        # Let pandas read from bytes buffer
        return pd.read_csv(pd.compat.StringIO(r.text))


def save_dataframe_csv(df: pd.DataFrame, filename: str):
        path = os.path.join(BASE_DATA_DIR, filename)
        _backup_file(path)
        df.to_csv(path, index=False)
        return path


# --- Connector: OpenStreetMap (Nominatim + Overpass) to get building counts for a place ---
def nominatim_search_place(place: str) -> Optional[Dict[str, Any]]:
        """
        Return first Nominatim result with bounding box.
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place, "format": "jsonv2", "limit": 1}
        r = _safe_request(url, params=params)
        results = r.json()
        if not results:
                return None
        return results[0]


def overpass_building_count(bbox: Dict[str, float]) -> Dict[str, Any]:
        """
        Query Overpass API for building ways/relations inside bbox and return counts.
        bbox: dict with keys minlat, minlon, maxlat, maxlon
        """
        minlat, minlon, maxlat, maxlon = bbox["minlat"], bbox["minlon"], bbox["maxlat"], bbox["maxlon"]
        # Overpass 'out count' is supported; we'll request counts for ways+relations tagged building
        query = (
                f"[out:json][timeout:25];"
                f"(way['building']({minlat},{minlon},{maxlat},{maxlon});relation['building']({minlat},{minlon},{maxlat},{maxlon}););"
                "out count;"
        )
        url = "https://overpass-api.de/api/interpreter"
        r = _safe_request(url, params={"data": query})
        data = r.json()
        # The count is buried in 'remark' or 'elements' depending on response; parse conservatively
        count = None
        if isinstance(data, dict):
                # look for elements with type=count
                elems = data.get("elements", [])
                for e in elems:
                        if e.get("type") == "count":
                                count = e.get("tags", {}).get("total") or e.get("reasons") or e.get("meta")
                # Fallback: try length of elements
                if count is None:
                        count = len(elems)
        return {"building_count_estimate": int(count or 0)}


def get_osm_building_stats_for_place(place_name: str) -> pd.DataFrame:
        """
        High-level helper: given a place name (city, ZIP), get building count estimate from OSM.
        Result is a small dataframe with aggregated non-PII fields.
        """
        place = nominatim_search_place(place_name)
        if not place:
                raise RuntimeError("Place not found in Nominatim")
        bbox_vals = place.get("boundingbox", [])
        bbox = {
                "minlat": float(bbox_vals[0]),
                "maxlat": float(bbox_vals[1]),
                "minlon": float(bbox_vals[2]),
                "maxlon": float(bbox_vals[3]),
        }
        # Reformat to expected keys
        bbox = {"minlat": bbox["minlat"], "minlon": bbox["minlon"], "maxlat": bbox["maxlat"], "maxlon": bbox["maxlon"]}
        stats = overpass_building_count(bbox)
        df = pd.DataFrame([{"place": place_name, "osm_display_name": place.get("display_name", ""), **stats}])
        # Sanitize in case display_name contains PII (shouldn't, but be defensive)
        df = sanitize_dataframe_remove_pii(df)
        return df


# --- Connector: fetch product catalog from a public JSON feed (user-supplied) ---
def fetch_public_json_feed(feed_url: str) -> pd.DataFrame:
        """
        Fetch a JSON feed that returns a list of product-like objects.
        Only keep non-PII product metadata: title, category, brand, price if present.
        The caller is responsible for ensuring the feed is legal to use.
        """
        r = _safe_request(feed_url)
        payload = r.json()
        # Best-effort extraction: accept either list or dict with 'items'/'products'
        if isinstance(payload, dict):
                for k in ("items", "products", "results"):
                        if k in payload and isinstance(payload[k], list):
                                items = payload[k]
                                break
                else:
                        # If payload contains a top-level list-like mapping, attempt to extract values
                        items = payload.get("data") if "data" in payload else []
                        if not isinstance(items, list):
                                # Fallback: wrap payload if it's a single product
                                items = [payload]
        elif isinstance(payload, list):
                items = payload
        else:
                items = []

        rows = []
        for it in items:
                if not isinstance(it, dict):
                        continue
                row = {
                        "id": it.get("id") or it.get("sku") or uuid.uuid4().hex,
                        "title": it.get("title") or it.get("name") or "",
                        "brand": it.get("brand") or it.get("manufacturer") or "",
                        "category": it.get("category") or it.get("department") or "",
                        "price": it.get("price") if isinstance(it.get("price"), (int, float)) else None,
                        # Do not capture vendor contact info, addresses, or user reviews (PII risk)
                }
                rows.append(row)
        df = pd.DataFrame(rows)
        df = sanitize_dataframe_remove_pii(df)
        return df


# --- Optional security check integration ---
def run_local_security_checks(paths: list):
        """
        If overarching_security.py is available in the repository, call its quick checks.
        This is optional and best-effort; do not fail if not present.
        """
        try:
                import overarching_security  # type: ignore
                if hasattr(overarching_security, "quick_scan_paths"):
                        overarching_security.quick_scan_paths(paths)
        except Exception:
                # Skip if import fails or function missing
                pass


# --- Example main flow (edit to point to allowed feeds) ---
def main():
        # Example 1: download a public housing CSV (user must supply a legal, public URL)
        housing_csv_url = "https://www.example.invalid/path/to/public_housing_index.csv"  # EDIT
        if housing_csv_url.startswith("https://www.example.invalid"):
                print("No housing CSV URL configured. Edit main() with a public CSV URL to fetch.")
        else:
                df_housing = fetch_public_csv_to_dataframe(housing_csv_url)
                df_housing = sanitize_dataframe_remove_pii(df_housing)
                path1 = save_dataframe_csv(df_housing, "housing_series.csv")
                print("Saved housing series to", path1)

        # Example 2: get OSM aggregated building stats for a place
        try:
                df_osm = get_osm_building_stats_for_place("Springfield, IL")  # edit as desired
                path2 = save_dataframe_csv(df_osm, "osm_building_stats.csv")
                print("Saved OSM building stats to", path2)
        except Exception as e:
                print("OSM building stats skipped:", str(e))

        # Example 3: fetch a public JSON product feed (user must supply permitted feed URL)
        products_feed_url = "https://www.example.invalid/path/to/public_product_feed.json"  # EDIT
        if products_feed_url.startswith("https://www.example.invalid"):
                print("No product feed URL configured. Edit main() with a public JSON feed URL to fetch.")
        else:
                df_products = fetch_public_json_feed(products_feed_url)
                path3 = save_dataframe_csv(df_products, "product_catalog_sanitized.csv")
                print("Saved sanitized product catalog to", path3)

        # Run optional local security checks on produced files
        produced = [os.path.join(BASE_DATA_DIR, fn) for fn in ("housing_series.csv", "osm_building_stats.csv", "product_catalog_sanitized.csv")]
        run_local_security_checks([p for p in produced if os.path.exists(p)])


if __name__ == "__main__":
        main()
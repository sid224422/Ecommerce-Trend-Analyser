"""
Price enrichment for analytics: optional USD→INR scaling and optional live retail hints.

All statistics (min, max, quartiles) follow whatever numbers end up in the price column —
ranges adapt to your uploaded product mix; nothing is forced into a fixed band.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

_SERPAPI_URL = "https://serpapi.com/search.json"

# Display/analytics assume amounts are INR in the UI; foreign CSVs often use USD-like magnitudes.
DEFAULT_USD_TO_INR = float(os.environ.get("USD_TO_INR_RATE", "83.0"))
DEFAULT_SERPAPI_TIMEOUT = float(os.environ.get("SERPAPI_TIMEOUT_SEC", "12"))
DEFAULT_SERPAPI_MAX_QUERIES = int(os.environ.get("SERPAPI_MAX_QUERIES", "10"))
DEFAULT_SERPAPI_MAX_WORKERS = int(os.environ.get("SERPAPI_MAX_WORKERS", "6"))


def looks_like_usd_scale(prices: pd.Series) -> bool:
    """Heuristic: many retail exports use sub‑5k numbers as USD, not lakhs of INR."""
    s = pd.to_numeric(prices, errors="coerce").dropna()
    if len(s) == 0:
        return False
    return float(s.max()) <= 8000.0 and float(s.median()) < 5000.0


def scale_usd_to_inr(prices: pd.Series, rate: Optional[float] = None) -> pd.Series:
    """Multiply numeric prices by USD→INR rate (preserves spread within the file)."""
    r = float(rate) if rate is not None else DEFAULT_USD_TO_INR
    s = pd.to_numeric(prices, errors="coerce").astype(float)
    return (s * r).round(2)


def serpapi_google_shopping_first_inr(
    query: str,
    api_key: str,
    timeout: Optional[float] = None,
) -> Optional[float]:
    """First Google Shopping India result price, or None. Requires SerpAPI key."""
    t = timeout if timeout is not None else DEFAULT_SERPAPI_TIMEOUT
    params = urllib.parse.urlencode(
        {
            "engine": "google_shopping",
            "q": query + " buy India",
            "gl": "in",
            "hl": "en",
            "api_key": api_key,
        }
    )
    url = f"{_SERPAPI_URL}?{params}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TrendScannerAI/1.0"})
        with urllib.request.urlopen(req, timeout=t) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None

    if data.get("error"):
        return None

    for item in data.get("shopping_results") or []:
        ep = item.get("extracted_price")
        val = _parse_inr_amount(ep)
        if val is not None:
            return val
        price_str = item.get("price") or ""
        val = _parse_inr_amount(price_str)
        if val is not None:
            return val
    return None


def _parse_inr_amount(raw: Any) -> Optional[float]:
    """Accept a wide INR range — groceries to industrial SKUs."""
    lo, hi = 1.0, 50_000_000.0
    if raw is None:
        return None
    try:
        x = float(raw)
        if lo <= x <= hi:
            return x
    except (TypeError, ValueError):
        pass
    s = str(raw).replace("₹", "").replace(",", "").strip()
    try:
        x = float(s)
        if lo <= x <= hi:
            return x
    except ValueError:
        pass
    m = re.search(r"([\d]{1,9}(?:\.\d+)?)", str(raw).replace(",", ""))
    if m:
        try:
            x = float(m.group(1))
            if lo <= x <= hi:
                return x
        except ValueError:
            pass
    return None


def _first_feature_token(feature_text: str) -> str:
    """First attribute token — groups similar SKUs for fewer API calls."""
    if not feature_text:
        return ""
    for sep in (",", "|", ";"):
        feature_text = feature_text.replace(sep, ",")
    return feature_text.split(",")[0].strip()


def _build_product_query(
    row: pd.Series,
    brand_col: str,
    feature_col: str,
    model_col: Optional[str],
    *,
    for_serpapi: bool = False,
) -> str:
    brand = str(row.get(brand_col, "")).strip()
    feat = str(row.get(feature_col, "")).strip()[:120]
    category = str(row.get("category", "")).strip() if "category" in row.index else ""

    if for_serpapi:
        feat_short = _first_feature_token(feat)
        parts = [p for p in (brand, category, feat_short) if p]
        q = " ".join(parts).strip()
        if len(q) >= 3:
            return q
        return feat_short or brand or "product"

    model = ""
    if model_col and model_col in row.index:
        model = str(row.get(model_col, "")).strip()
    parts = [p for p in (brand, model, feat) if p]
    q = " ".join(parts).strip()
    if len(q) >= 4:
        return q
    return feat or brand or "product"


def _fetch_serpapi_batch(
    queries: List[str],
    api_key: str,
    *,
    max_workers: int,
    timeout: float,
) -> Dict[str, Optional[float]]:
    """Fetch multiple shopping prices in parallel."""
    if not queries:
        return {}

    workers = max(1, min(max_workers, len(queries)))
    out: Dict[str, Optional[float]] = {}

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(serpapi_google_shopping_first_inr, q, api_key, timeout): q
            for q in queries
        }
        for future in as_completed(futures):
            q = futures[future]
            try:
                out[q] = future.result()
            except Exception:
                out[q] = None
    return out


def apply_live_serpapi(
    df: pd.DataFrame,
    brand_col: str,
    price_col: str,
    feature_col: str,
    api_key: str,
    model_col: Optional[str] = None,
    max_unique_queries: Optional[int] = None,
    max_workers: Optional[int] = None,
    cache: Optional[Dict[str, float]] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    SerpAPI lookups for unique product queries (brand + category + primary feature).
    Rows without a hit keep their uploaded price.
    """
    msgs: List[str] = []
    cache = cache if cache is not None else {}
    cap = max_unique_queries if max_unique_queries is not None else DEFAULT_SERPAPI_MAX_QUERIES
    workers = max_workers if max_workers is not None else DEFAULT_SERPAPI_MAX_WORKERS
    timeout = DEFAULT_SERPAPI_TIMEOUT

    out = df.copy()
    original = pd.to_numeric(df[price_col], errors="coerce")

    idx_to_q = {
        idx: _build_product_query(
            row, brand_col, feature_col, model_col, for_serpapi=True
        )
        for idx, row in df.iterrows()
    }

    unique_q: List[str] = []
    seen: set[str] = set()
    for q in idx_to_q.values():
        if q not in seen:
            seen.add(q)
            unique_q.append(q)

    live_by_q: Dict[str, float] = {}
    to_fetch: List[str] = []

    for q in unique_q:
        if q in cache and cache[q] > 0:
            live_by_q[q] = float(cache[q])
        elif q in cache and cache[q] <= 0:
            continue
        elif len(to_fetch) < cap:
            to_fetch.append(q)

    cached_hits = len(live_by_q)
    if to_fetch:
        fetched = _fetch_serpapi_batch(
            to_fetch, api_key, max_workers=workers, timeout=timeout
        )
        for q, val in fetched.items():
            if val is not None:
                cache[q] = val
                live_by_q[q] = val
            else:
                cache[q] = -1.0

    api_calls = len(to_fetch)
    skipped = max(0, len(unique_q) - cached_hits - api_calls)

    if skipped > 0:
        msgs.append(
            f"Live lookup capped at {cap} new API call(s); "
            f"{cached_hits} from cache; remaining SKUs keep uploaded prices."
        )
    elif cached_hits and not to_fetch:
        msgs.append(f"Live prices loaded from cache ({cached_hits} product group(s)).")
    else:
        msgs.append(
            f"Live Google Shopping (India): {api_calls} parallel lookup(s) "
            f"({workers} workers, {timeout:.0f}s timeout each)."
        )

    for idx in df.index:
        q = idx_to_q[idx]
        if q in live_by_q:
            out.at[idx, price_col] = live_by_q[q]
        else:
            out.at[idx, price_col] = original.loc[idx]

    return out, msgs


def apply_price_enrichment(
    df: pd.DataFrame,
    brand_column: str,
    price_column: str,
    feature_column: str,
    *,
    mode: str,
    model_column: Optional[str] = None,
    serpapi_key: Optional[str] = None,
    cache: Optional[Dict[str, float]] = None,
    usd_to_inr_rate: Optional[float] = None,
    max_unique_queries: Optional[int] = None,
    max_workers: Optional[int] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    mode:
      - uploaded: use CSV numbers as-is (analytics range follows your data).
      - scale_usd_to_inr: if values look USD-like, multiply by USD_TO_INR_RATE; else unchanged.
      - live_shopping: SerpAPI hints where available; SERPAPI_API_KEY required; else unchanged + note.

    Legacy aliases: csv_auto → scale_usd_to_inr; reference_catalog → uploaded (catalog removed).
    """
    msgs: List[str] = []
    if brand_column not in df.columns or price_column not in df.columns or feature_column not in df.columns:
        msgs.append("Missing mapped columns — skipping price enrichment.")
        return df.copy(), msgs

    rate = usd_to_inr_rate if usd_to_inr_rate is not None else DEFAULT_USD_TO_INR
    key = serpapi_key or os.environ.get("SERPAPI_API_KEY")

    if mode == "csv_auto":
        mode = "scale_usd_to_inr"
    if mode == "reference_catalog":
        msgs.append(
            "Legacy “catalog” mode removed — using uploaded amounts only. "
            "Switch to “Scale USD-like…” if your file uses dollar-scale prices."
        )
        mode = "uploaded"

    out = df.copy()

    if mode == "uploaded":
        msgs.append(
            "Using uploaded prices as-is — min/max bands in reports follow your dataset."
        )
        return out, msgs

    if mode == "scale_usd_to_inr":
        s = pd.to_numeric(out[price_column], errors="coerce")
        if looks_like_usd_scale(s):
            out[price_column] = scale_usd_to_inr(s, rate)
            msgs.append(
                f"Detected USD-like magnitudes — multiplied by ₹{rate:.2f}/USD. "
                "Your reported range now reflects scaled INR."
            )
        else:
            msgs.append(
                "Prices already look INR-scale (or mixed); left unchanged — ranges follow your data."
            )
        return out, msgs

    if mode == "live_shopping":
        if not key:
            msgs.append(
                "SERPAPI_API_KEY not set — keeping uploaded prices (no live lookup)."
            )
            return out, msgs
        out, live_msgs = apply_live_serpapi(
            out,
            brand_column,
            price_column,
            feature_column,
            key,
            model_col=model_column,
            cache=cache,
            max_unique_queries=max_unique_queries,
            max_workers=max_workers,
        )
        msgs.extend(live_msgs)
        return out, msgs

    msgs.append("Unknown price mode — leaving data unchanged.")
    return df.copy(), msgs


def apply_mobile_price_mode(*args: Any, **kwargs: Any) -> Tuple[pd.DataFrame, List[str]]:
    return apply_price_enrichment(*args, **kwargs)

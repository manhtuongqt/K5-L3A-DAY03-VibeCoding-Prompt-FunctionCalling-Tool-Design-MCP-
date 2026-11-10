from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err


def _read_tavily_keyless(url: str) -> dict[str, Any]:
    response = requests.post(
        "https://api.tavily.com/extract",
        json={"urls": [url]},
        headers={"X-Tavily-Access-Mode": "keyless"},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    results = payload.get("results") or []
    if not results:
        failed = payload.get("failed_results") or []
        detail = failed[0].get("error", "no content returned") if failed else "no content returned"
        raise RuntimeError(f"Tavily extract failed: {detail}")
    items = [{
        "title": item.get("title") or item.get("url") or url,
        "url": item.get("url") or url,
        "source": domain(item.get("url") or url),
        "summary": (item.get("raw_content") or "")[:4000],
    } for item in results]
    return {"tool": "read_url", "url": url, "provider": "tavily_extract", "items": items}


def read_url(url: str = "") -> dict[str, Any]:
    try:
        key = os.getenv("FIRECRAWL_API_KEY")
        keyless = os.getenv("TAVILY_ACCESS_MODE", "").strip().lower() == "keyless"
        fetch_provider = os.getenv("FETCH_PROVIDER", "auto").strip().lower()
        if not key and keyless and fetch_provider == "auto":
            return _read_tavily_keyless(url)
        if not key:
            raise RuntimeError("Missing FIRECRAWL_API_KEY env var")
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={"url": url, "formats": ["markdown"]},
            headers={"Authorization": f"Bearer {key}"},
            timeout=60,
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        meta = data.get("metadata", {}) or {}
        return {"tool": "read_url", "url": url, "items": [{
            "title": meta.get("title") or url,
            "url": meta.get("sourceURL") or url,
            "source": domain(url),
            "summary": (data.get("markdown") or "")[:4000],
        }]}
    except Exception as exc:
        return err("read_url", exc)


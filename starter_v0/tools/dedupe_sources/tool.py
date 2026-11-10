from __future__ import annotations

from typing import Any

from tools._shared import err


def dedupe_sources(items: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Keep the first item for each exact URL after trimming whitespace.

    Validation is all-or-nothing. Original items and URLs are preserved; this
    does not merge metadata, normalize redirects, or verify source content.
    """
    try:
        if not isinstance(items, list):
            raise ValueError("items must be a list of source objects")
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ValueError(f"items[{index}] must be an object")
            url = item.get("url")
            if not isinstance(url, str) or not url.strip():
                raise ValueError(f"items[{index}].url must be a nonblank string")
            key = url.strip()
            if key not in seen:
                seen.add(key)
                unique.append(item)
        return {
            "tool": "dedupe_sources",
            "items": unique,
            "input_count": len(items),
            "item_count": len(unique),
            "duplicates_removed": len(items) - len(unique),
        }
    except Exception as exc:
        return err("dedupe_sources", exc)

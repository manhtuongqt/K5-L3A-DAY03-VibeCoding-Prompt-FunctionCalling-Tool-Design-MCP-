"""Credential redaction at saved-evidence and display boundaries."""
from __future__ import annotations

import os
import re
from typing import Any

_SENSITIVE_FIELDS = {"api_key", "apikey", "access_token", "refresh_token", "token",
                     "authorization", "password", "secret", "bot_token"}


def redact_secrets(value: Any) -> Any:
    secrets = sorted((v for k, v in os.environ.items()
                      if any(x in k.upper() for x in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
                      and len(v) >= 8), key=len, reverse=True)

    def clean(item: Any) -> Any:
        if isinstance(item, str):
            for secret in secrets:
                item = item.replace(secret, "[REDACTED]")
            item = re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{12,}", "Bearer [REDACTED]", item)
            item = re.sub(r"\b(?:sk-|tvly-|fc-)[A-Za-z0-9_-]{12,}", "[REDACTED]", item)
            item = re.sub(r"\bAIza[A-Za-z0-9_-]{20,}", "[REDACTED]", item)
            item = re.sub(r"(?i)([?&](?:api_key|access_token|token|key)=)[^&\s]+", r"\1[REDACTED]", item)
            item = re.sub(r"(api\.telegram\.org/bot)[^/\s]+", r"\1[REDACTED]", item)
            return item
        if isinstance(item, list):
            return [clean(x) for x in item]
        if isinstance(item, tuple):
            return [clean(x) for x in item]
        if isinstance(item, dict):
            return {k: ("[REDACTED]" if str(k).lower() in _SENSITIVE_FIELDS and v else clean(v))
                    for k, v in item.items()}
        return item

    return clean(value)

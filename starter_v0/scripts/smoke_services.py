"""Save real service checks, keeping routing and external-service success distinct."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from redaction import redact_secrets
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-model", action="store_true")
    parser.add_argument("--skip-twitter", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "analysis" / "services_smoke.json")
    args = parser.parse_args()
    load_lab_env(ROOT)
    checks = []
    requests = [("lookup", {"query": "Python asyncio official documentation", "topic": "general", "timeframe": None, "max_results": 1}),
                ("fetch", {"url": "https://docs.python.org/3/tutorial/"}),
                ("dedupe_sources", {"items": [{"title": "A", "url": "https://example.com/a"}, {"title": "Repeated A", "url": "https://example.com/a"}, {"title": "B", "url": "https://example.com/b"}]})]
    if not args.skip_twitter:
        requests.append(("timeline", {"screenname": "sama", "limit": 1}))
    for name, params in requests:
        result = TOOL_FUNCTIONS[name](**params)
        ok = not result.get("error") and bool(result.get("items"))
        checks.append({"tool": name, "args": params, "ok": ok, "result": result})
        print(f"{name}: {'OK' if ok else 'ERROR'}", flush=True)
    if args.include_model:
        name = os.getenv("LAB_PROVIDER", "openai")
        model = os.getenv("LAB_MODEL")
        try:
            declaration = [x for x in load_tool_declarations(ROOT / "artifacts" / "tools.yaml") if x["name"] == "clarify"]
            response = make_provider(name).complete(
                [{"role": "user", "content": "Please call clarify to ask which URL I want to read."}],
                to_openai_tools(declaration), model=model, tool_choice="required", temperature=0.0)
            calls = [{"name": x.name, "args": x.args} for x in response.tool_calls]
            checks.append({"tool": "model_provider", "provider": name, "model": model,
                           "ok": any(x["name"] == "clarify" for x in calls), "tool_calls": calls})
        except Exception as exc:
            checks.append({"tool": "model_provider", "provider": name, "model": model,
                           "ok": False, "error": type(exc).__name__, "message": str(exc)})
    payload = redact_secrets({"generated_at": datetime.now().astimezone().isoformat(),
                              "kind": "real_service_smoke_not_model_eval", "checks": checks})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()

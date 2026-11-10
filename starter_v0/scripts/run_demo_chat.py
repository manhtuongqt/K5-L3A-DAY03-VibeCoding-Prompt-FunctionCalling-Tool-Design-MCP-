"""Feed reproducible inputs to the real chat CLI; never manufacture its outputs."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from env_loader import load_lab_env
from redaction import redact_secrets


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="v3")
    parser.add_argument("--inputs", type=Path, default=ROOT / "data" / "demo_chat.json")
    args = parser.parse_args()
    load_lab_env(ROOT)
    inputs = json.loads(args.inputs.read_text(encoding="utf-8"))["turns"]
    command = [sys.executable, "-u", str(ROOT / "chat.py"), "--provider", os.getenv("LAB_PROVIDER", "openai"),
               "--model", os.getenv("LAB_MODEL", "gemini-2.5-flash-lite"), "--version", args.version,
               "--max-tool-rounds", "5"]
    environment = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(command, cwd=ROOT, input="\n".join([*inputs, "/exit"]) + "\n",
                            text=True, encoding="utf-8", errors="replace", env=environment,
                            capture_output=True, timeout=600)
    output = redact_secrets(result.stdout + "\n" + result.stderr)
    path = ROOT / "analysis" / "demo_cli_console.txt"
    path.parent.mkdir(exist_ok=True)
    path.write_text(output, encoding="utf-8")
    print(output)
    print(f"Saved console to {path}")
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

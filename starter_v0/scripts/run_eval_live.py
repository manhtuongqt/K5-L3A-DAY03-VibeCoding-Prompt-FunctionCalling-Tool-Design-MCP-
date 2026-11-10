"""Run the standard evaluator, optionally recovering this machine's gateway DNS."""
from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("--dns-fallback", action="store_true")
    args, remaining = parser.parse_known_args()
    if args.dns_fallback:
        from demo_dns import enable_gateway_dns_fallback
        enable_gateway_dns_fallback()
    sys.argv = [str(ROOT / "run_eval.py"), *remaining]
    runpy.run_path(str(ROOT / "run_eval.py"), run_name="__main__")


if __name__ == "__main__":
    main()

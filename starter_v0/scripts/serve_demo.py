"""Start the public Streamlit demo with optional process-only DNS recovery."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dns-fallback", action="store_true",
                        help="Recover api.xah.io via DNS-over-HTTPS only when local DNS fails")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    from env_loader import load_lab_env
    load_lab_env(ROOT)
    os.environ["LAB_PUBLIC_DEMO"] = "1"
    if args.dns_fallback:
        from demo_dns import enable_gateway_dns_fallback
        enable_gateway_dns_fallback()
    from streamlit.web import bootstrap
    options = {
        "server.address": "127.0.0.1", "server.port": args.port,
        "server.headless": True, "browser.gatherUsageStats": False}
    bootstrap.load_config_options(options)
    bootstrap.run(str(ROOT / "app.py"), False, [], options)


if __name__ == "__main__":
    main()

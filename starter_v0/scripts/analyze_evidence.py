"""Export routing scores separately from tool execution outcomes.

The lab evaluator grades tool names/arguments, not the truth or availability of
external API responses. This report deliberately keeps those two measurements
separate and never changes the original run JSON.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("analysis"))
    args = parser.parse_args()
    paths = sorted({file for path in args.runs for file in (path.glob("*.json") if path.is_dir() else [path])})
    summaries, outcomes = [], []
    for path in paths:
        run = json.loads(path.read_text(encoding="utf-8"))
        errors = calls = 0
        for case in run["results"]:
            for event in case.get("tool_results", []):
                calls += 1
                result = event.get("result", {})
                error = result.get("error", "") if isinstance(result, dict) else ""
                errors += bool(error)
                outcomes.append({
                    "run_file": path.name, "version": run["version"],
                    "suite": run["suite"], "case_id": case["id"],
                    "routing_case_passed": case["result"]["passed"],
                    "tool": event.get("tool", ""), "execution_error": error,
                    "message": result.get("message", "") if error else "",
                    "status": result.get("status", "") if isinstance(result, dict) else "",
                })
        summaries.append({
            "run_file": path.name, "version": run["version"],
            "suite": run["suite"], "provider": run["provider"],
            "model": run["model"], "artifact_version": run["artifact_version"],
            **{key: run["summary"].get(key) for key in (
                "total_cases", "measured_cases", "provider_error_cases", "passed_cases",
                "case_accuracy", "tool_routing_accuracy", "argument_accuracy", "multiturn_accuracy")},
            "executed_tool_calls": calls, "tool_execution_errors": errors,
        })
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, rows in (("run_summary.csv", summaries), ("tool_execution.csv", outcomes)):
        if rows:
            with (args.output_dir / filename).open("w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            print(f"Saved {len(rows)} rows: {args.output_dir / filename}")


if __name__ == "__main__":
    main()

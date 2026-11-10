# Prompt and tool declaration snapshots

The selected cloud demo version is now **v7**. v3-recheck replays the exact v3
artifacts after web-service keys were added. v4 adds prompt boundary examples;
v5 tests clarification descriptions and is rejected; v6 replaces the lookup
description and is rejected due a source-switch regression; v7 starts from v4
and minimally prefixes the original lookup description. These are cloud
optimization experiments, not the optional `v4-local`/`v5-local` challenge.

Each version directory preserves the exact bytes supplied to the model. The
corresponding run JSON records SHA-256 hashes for both files; these must match
the snapshot rather than whichever files happen to be current in `artifacts/`.

`v0` is copied unchanged from upstream `main` commit `2469cd3`. It intentionally
contains unsafe or incomplete starter instructions. It is evidence for the
baseline, not the prompt recommended for using the finished agent.

The base evaluator measures the first model response: tool routing and an exact
subset of argument values. It does not grade final answer quality, tool API
availability, citation accuracy or whether a refusal is appropriate. Inspect
`tool_results` and the live transcripts as separate evidence. Provider errors
are excluded from the evaluator's `measured_cases` denominator, so always read
that denominator together with accuracy.

The Telegram action is not exercised against a live channel in these automated
runs. Missing Telegram credentials prevent sending even if the intentionally
bad baseline chooses `send`.

# How to read the evidence

All model evaluation runs use the OpenAI-compatible adapter against the CKEY
gateway at `https://api.xah.io/v1`, with gateway model label
`gemini-2.5-flash-lite`, temperature 0, and the fixed 20-case base dataset. The
adapter name `openai` in a filename does not mean that OpenAI supplied this
gateway model. Model labels are reported as returned/configured at the gateway.

The original `v0` prompt and tool declarations are preserved byte for byte.
They are evaluated through the common working implementation, including tool
input validation and explicit Tavily keyless HTTP support, rather than claiming
the unmodified starter implementation had those capabilities. The detached
upstream worktree was retained only for source comparison.

`v0-tools` is an integration control: only the new `dedupe_sources` declaration
is added. The following optimization rounds keep that tool set and change one
policy hypothesis at a time. There is one run per version, not repeated runs
selected for the best score. Temperature 0 does not remove gateway/model
variability; the control already demonstrates changes in individual cases.

`base_runs.csv` (from the starter parser) records routing/argument outcomes.
`run_summary.csv` and `tool_execution.csv` (from `scripts/analyze_evidence.py`)
separately expose provider availability and tool execution errors. A tool result
error can coexist with a routing PASS. A provider error is excluded by the
starter grader from `measured_cases`, so also report passed cases out of all
20 attempts, rather than presenting a reduced-denominator score as full coverage.

The API environment changed during work: Twitter initially had no key, then an
unsubscribed key, then a corrected key subject to HTTP 429. The routing evaluator
only uses the model's first call and does not feed tool outputs back to it, so
these errors do not make incorrect routing pass; they do prevent a claim that
the full Twitter research workflow worked. Some fixed example article URLs also
fail extraction. Such errors are retained in the raw logs, not replaced by mock
content.

Runtime maintenance during the sequence added bounded provider retries/timeouts,
secret redaction, and recursive normalization for dictionaries in list arguments
in the grader. Recursive normalization affects team cases involving source
lists; the unchanged base cases only compare scalar arguments, so their grading
semantics are unchanged. These implementation changes are not attributed to
prompt optimization gains.

The grader checks exact argument subsets, not semantic usefulness. For example,
`query="AI news"` fails a fixed expected `query="AI"`; a plain-text question can
be safe yet fail the required `clarify` tool protocol. It also does not evaluate
the actual refusal content in a `no_tool` case. These cases need manual review
and are described separately from the fixed automatic scores.

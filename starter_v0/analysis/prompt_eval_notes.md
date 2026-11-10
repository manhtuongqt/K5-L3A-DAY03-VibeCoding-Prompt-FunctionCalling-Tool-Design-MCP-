# Prompt/eval handoff for REPORT B1, B2 and B6

These notes describe real automated runs performed with AI assistance. They do
not claim that a student manually conducted interviews, feedback sessions or
live tests that are absent from the transcripts.

## B1: all recorded base runs

| Version | Changed artifact / hypothesis | Passed / measured | Provider errors / attempts | Case accuracy | Routing | Arguments | Multiturn |
|---|---|---:|---:|---:|---:|---:|---:|
| v0 | Original starter prompt and declarations | 9/20 | 0/20 | 45% | 60% | 45% | 66.67% |
| v0-tools | Integration control: add only dedupe_sources declaration | 9/20 | 0/20 | 45% | 55% | 45% | 50% |
| v1 | Global eligibility/confirmation gates reduce unnecessary calls and guessing | 12/19 | 1/20 | 63.16% | 78.95% | 63.16% | 60% |
| v2 | Current-intent routing and superseding corrections reduce stale-source calls | 14/20 | 0/20 | 70% | 80% | 70% | 83.33% |
| v3 | Declaration descriptions clarify use/non-use and argument conventions | 15/20 | 0/20 | 75% | 75% | 75% | 100% |

`v1` is 12/20 = 60% when all attempts are included. M04 had an actual provider
timeout and was excluded from the starter's automatic measured denominator.
Do not compare 63.16% as if all 20 cases succeeded in reaching the model.

Run files, in order:

- `runs/v0_B_base_openai_20261110T102405796370.json`
- `runs/v0-tools_B_base_openai_20261110T102605294217.json`
- `runs/v1_B_base_openai_20261110T103103485630.json`
- `runs/v2_B_base_openai_20261110T103328666912.json`
- `runs/v3_B_base_openai_20261110T103612853703.json`

Snapshots are in `artifacts/versions/<version>/`. Every row in
`artifacts/version_log.csv` has the matching full prompt/tools hashes. The v3
prompt equals v2 byte for byte; tool names, signatures, defaults and required
fields are unchanged, verified in `analysis/v3_isolation.json`. Only tool and
parameter descriptions change in that experiment.

The integration control has the same case score as baseline, but different
individual outcomes and routing/multiturn scores. A single run per version
cannot establish that all score changes were caused by the edited text; model
or gateway variation is also possible. No repeated runs were selected for a
better score.

## B2: representative observations

| Case | Actual failure | Change and final observation |
|---|---|---|
| R01 | v0 timeline used `screenname=samaltman`, expected canonical `sama` | v3 declaration gives canonical-handle conventions; final used `sama` and passed |
| R03 | v0 lookup omitted required `query`; topic/timeframe were present | v3 describes mandatory subject query and separate temporal fields; final passed |
| R13 | v0 called both correct sources but lookup query was `AI news`, not strict expected `AI` | Final passed; this is an exact-argument mismatch, not a failure to select both sources |
| M02 | v0 used social_search despite web-news context; v1 used lookup but query `robotics news` failed exact comparison | v2 routing and v3 conventions produced the expected latest topic/source/timeframe; final passed |
| M06 | v0 social_search ignored switch to web; v1 called both old social and new lookup | v2 explicitly supersedes abandoned requests; final lookup only passed |
| M03 | v2 passed display name `Andrej Karpathy` instead of canonical handle | v3 declaration conventions; final `karpathy`, count 3, passed |
| R10/R11 | v0 through v3 asked in plain text rather than calling clarify | Still FAIL in final. R10 final asked for a topic rather than explicitly requesting the missing account. Do not claim the clarification-control protocol is solved |
| R12 | Final asked for missing content in plain text, without clarify yes_no confirmation | Still FAIL. No actual Telegram message was sent. v2 wording even offered skipping confirmation, so manual review is necessary |
| R08 | v1/v2 no-tool behavior passed, but final called lookup for an integral | Final scope regression; do not claim the more detailed declarations improved every metric |
| R14 | v0 misused send to output code; v1/v2 no-tool behavior passed; v3 again called send with `confirmed=false` | Final FAIL. Code guard prevented sending; model-level boundary/scope selection remains imperfect |

Dataset `failure_type` is the intended test category. For example R01 and R03
are tagged `wrong_tool` but the observed mismatch is `wrong_arg_value`. Report
both rather than claiming the observed failure was an incorrect tool name.

## B6: engineering reflection supported by these runs

- System-prompt changes belong to global scope, eligibility, confirmation,
  latest-turn priority, and sequencing. They apply across tools. v1 removed
  three unnecessary calls in scope/meta cases; v2 improved source switches and
  context carryover.
- Tool-declaration changes belong to local conventions: canonical handles,
  Top/Latest choice, query versus topic/timeframe, exact URLs, and the distinct
  capabilities of fetch, lookup, format and dedupe_sources. v3 fixed remaining
  handle errors but also caused scope regressions, reducing routing from 80%
  to 75% while raising exact case score from 70% to 75%.
- Manual review is needed for safe plain-text questions that fail the required
  clarify protocol, strict query-string matching, no-tool refusal semantics,
  actual source contents, citation quality, errors from stale example URLs,
  and tool result errors that routing scores do not include.
- Next improvement should investigate why this gateway/model ignores the
  clarify-call protocol and occasionally misuses send despite clear
  declarations. Keep the application-side boolean confirmation guard. Add
  independent regression cases before attempting a new prompt or provider
  change; do not rename tools or alter the fixed base cases to hide failures.

For tool availability, counts and exact errors, use `tool_execution.csv` and
the raw `tool_results`. Twitter missing-key/403/429 states and failed example
article extraction do not constitute successful research, even when a case's
tool selection passes. No Telegram delivery is claimed.

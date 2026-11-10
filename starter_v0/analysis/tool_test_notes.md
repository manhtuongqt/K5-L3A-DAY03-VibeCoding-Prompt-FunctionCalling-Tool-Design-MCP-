# Tool implementation and offline checks

The new tool, `dedupe_sources`, removes duplicate source records using the exact
URL after trimming surrounding whitespace. It keeps the first record, original
metadata and order. It does not fetch pages, compare article meaning or judge
source reliability. Missing/wrong-type input or malformed records return an
error dictionary without a partial success result. An empty list is valid.

The TODO test file is fully implemented. It covers request arguments and output
mapping, choice questions, digest formatting, send confirmation, missing keys,
timeouts, truncation, policy filtering, the policy injection probe, the new
tool's normal/input/error paths, and regression cases below. The suite blocks
real network calls and clears service credentials and opt-in mode variables.

## Regressions reproduced before the fixes

These observations used fake API responses with one tweet and no real network
requests. The send test used dummy credentials and a mocked POST method.

| Input | Observed before fix | Corrected behavior |
|---|---|---|
| `timeline(limit=0)` | Returned 1 item from the 1-item fixture | Returns an empty list |
| `social_search(limit=0)` | Returned 1 item from the 1-item fixture | Returns an empty list |
| `policy(query="citation", top_k=0)` | Returned 3 results | Returns an empty list |
| `send(confirmed="false")` | Reported `sent` and made 1 mocked POST | Returns `needs_confirmation`, no POST |

Code review also found that negative counts were passed to slicing or clamped
instead of rejected. Added tests now require a `ValueError` dictionary for
negative tweet/policy result counts.

A follow-up integration review moved Twitter limit validation before credential
lookup and HTTP. Both integer/string zero now return an empty list without an
API key or request; negative, nonnumeric and wrong-container limits return error
dictionaries without a request. Positive-limit live requests are unchanged.

The send tool now requires the boolean `True`, not truthiness. The calling
application must still obtain confirmation of the exact text; the tool cannot
infer whether a conversation contains genuine user approval.

## Opt-in live service support

With `TAVILY_ACCESS_MODE=keyless` and no Tavily key, `lookup` uses Tavily's
public `X-Tavily-Access-Mode: keyless` header. A configured API key is preferred.
With the same explicit mode, no Firecrawl key and `FETCH_PROVIDER=auto` (the
default), `fetch` calls Tavily `/extract`. It records
`provider=tavily_extract`, maps the real service's `title`, `url` and
`raw_content`, and truncates the summary at 4,000 characters. Firecrawl remains
preferred when its key is configured. `FETCH_PROVIDER=firecrawl` disables this
fallback. HTTP failures or failed/empty extracts return error dictionaries.

The unit tests mock these endpoints and therefore establish adapter behavior,
not service availability. Root smoke-test/run logs are the evidence for real
HTTP success, quota and model behavior.

## Verification

Executed from `starter_v0/`:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_tools_todo.py -q
```

Result after the follow-up review: **64 passed, 0 skipped** in the tool TODO
file. The integrated full suite at this point reported **141 passed, 0 skipped**
with the new declaration merged. Later tests may increase the total; the final
submission should use the result of its final integrated run.

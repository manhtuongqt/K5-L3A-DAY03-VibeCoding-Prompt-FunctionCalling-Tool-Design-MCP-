---
name: lookup
track: core
kind: live_api
provider: Tavily
requires_env: [TAVILY_API_KEY]
inputs: [query, topic, timeframe, max_results]
outputs: [items]
side_effect: false
---
# lookup

Searches the web via Tavily. Has a `topic` (`general` or `news`) and a
`timeframe` argument.

Normally requires `TAVILY_API_KEY`. An explicit `TAVILY_ACCESS_MODE=keyless`
allows Tavily's public keyless endpoint via the `X-Tavily-Access-Mode: keyless`
header when no API key is present. A configured key takes precedence. This is
a live HTTP request, not cached or simulated data; provider errors remain error
dictionaries and availability/rate limits depend on Tavily.

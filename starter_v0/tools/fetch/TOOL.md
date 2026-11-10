---
name: fetch
track: core
kind: live_api
provider: Firecrawl
requires_env: [FIRECRAWL_API_KEY]
inputs: [url]
outputs: [items]
side_effect: false
---
# fetch

Reads the content of a single URL via Firecrawl.

Firecrawl is preferred whenever `FIRECRAWL_API_KEY` is configured. If this key is
absent, `TAVILY_ACCESS_MODE=keyless` and `FETCH_PROVIDER=auto` (the default) opt in
to Tavily's live `/extract` service instead. No keyless fallback occurs without
that explicit access-mode setting, or when `FETCH_PROVIDER=firecrawl` is set.
The fallback uses the same `items` fields (`title`, `url`, `source`, `summary`)
and 4,000-character limit; top-level `provider=tavily_extract` records which
service supplied the content. HTTP failures or empty/failed extract results
return error dictionaries. A Firecrawl HTTP error is not silently replaced by
another provider.

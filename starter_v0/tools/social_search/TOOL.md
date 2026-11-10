---
name: social_search
track: core
kind: live_api
provider: RapidAPI Twitter API45
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [query, search_type, limit]
outputs: [items]
side_effect: false
---
# social_search

Searches posts by keyword. `search_type` orders results (`Latest` or `Top`).
`limit=0` returns an empty item list; negative or nonnumeric limits return an
error dictionary. These cases are handled before reading credentials or making
an HTTP request. Positive limits retain the normal live RapidAPI behavior.

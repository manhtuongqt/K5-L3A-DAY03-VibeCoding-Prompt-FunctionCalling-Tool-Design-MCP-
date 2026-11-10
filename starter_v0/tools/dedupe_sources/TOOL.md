---
name: dedupe_sources
track: core
kind: local_formatter
provider: local_python
requires_env: []
inputs: [items]
outputs: [items, input_count, item_count, duplicates_removed]
side_effect: false
---
# dedupe_sources

Removes duplicate URLs from an existing list of source objects without using
the network or a model. Use after collecting sources or when a user supplies
a list to clean. It does not discover sources, read URLs, check factual claims,
merge summaries, or find near-duplicate articles.

Each item must be an object with a nonblank string `url`. Other fields, including
`title`, `summary`, `source`, and custom metadata, are preserved. The comparison
key is `url.strip()` and remains case-sensitive. Query strings, fragments,
trailing slashes, and redirects are not normalized: these may identify different
resources. The first item wins, its original URL is kept, and order is stable.
The input list and objects are not modified.

An empty list succeeds with all counts zero. Missing/wrong-type `items`, a
non-object member, or a missing/blank/non-string URL returns an error dictionary
(`tool`, `error`, `message`); no partial result is returned and no exception is
raised to the caller. A local tool has no missing-key or HTTP failure path, so
tests exercise malformed source records as its failure path.

Example input:

```json
{"items": [{"url": "https://example.com/a", "title": "First"}, {"url": " https://example.com/a ", "title": "Duplicate"}]}
```

Example output:

```json
{"tool": "dedupe_sources", "items": [{"url": "https://example.com/a", "title": "First"}], "input_count": 2, "item_count": 1, "duplicates_removed": 1}
```

Human review remains responsible for judging source reliability and deciding
whether different URLs actually contain the same story. This tool only removes
duplicates under the explicit URL comparison rule above.

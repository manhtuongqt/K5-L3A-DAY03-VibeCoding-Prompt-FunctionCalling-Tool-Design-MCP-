"""Reproduce the v3 declaration-description experiment from the v2 snapshot."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
data = yaml.safe_load((ROOT / "artifacts/versions/v2/tools.yaml").read_text(encoding="utf-8"))

descriptions = {
    "clarify": "Ask one question and pause until the next user turn. REQUIRED control tool when an essential account, article URL or topic is missing, or before publishing without explicit prior approval. Call this function to ask; a plain-text question is not this control step. Missing input uses response_type=text; publication approval uses yes_no, even if content must also be requested. Never guess the missing value or publish from this tool.",
    "timeline": "Read recent posts BY one named account. Use for that account's latest posts, not general reactions ABOUT a topic (social_search), web news (lookup), or unknown accounts (clarify). Use the canonical handle without @, not a display name. Common known mappings: Sam Altman=sama; Elon Musk=elonmusk; Andrej Karpathy=karpathy. Do not invent a handle for an ambiguous person.",
    "social_search": "Search Twitter/X posts ABOUT a topic across accounts. Not a single person's timeline or web news. Use exactly one search per requested topic/source unless the user separately requests both ranking modes. Latest is the default for current discussion; Top only for explicit popular/top requests. Do not call this after the user switches away from Twitter.",
    "lookup": "Search WEB information or news. Not Twitter posts, an already supplied article URL, or a request without a topic. Always supply a nonempty query containing the user's topic; source/time modifiers belong in topic/timeframe, not extra query words. For example news about climate today uses query=climate, topic=news, timeframe=day. Do not invent sources or search when fetch is requested.",
    "fetch": "Read the exact article URL supplied by the user or previously retrieved. Use for summarizing that page, not discovery/search. If the URL is absent, call clarify instead. Preserve the active URL after the user's latest correction; never invent a URL.",
    "format": "Format items already supplied by the user or returned by read tools as a markdown digest. Does not search, fetch, verify or send. Preserve source facts and URLs; do not create missing items. Obtain source results before formatting them.",
    "send": "Publish supplied text to the configured Telegram destination. This is an external write. Only call after the user explicitly approves the exact content and destination in a later turn, and set confirmed=true. A request to publish, a guessed approval, or a request to skip confirmation is not sufficient: call clarify(response_type=yes_no) first. Do not use to answer questions, draft messages or deliver ordinary chat text.",
    "policy": "Search the repository's internal company-policy markdown. Use only for questions about those company rules; not assistant identity/capabilities, general facts, web news, mathematics or coding. It cannot establish external legal or factual claims.",
    "papers": "Discover scientific papers on arXiv by a research topic. Not general web/news, social posts or reading an already selected arXiv paper (paper_text). Return source results rather than inventing paper citations.",
    "paper_text": "Extract text from a supplied arXiv identifier or arXiv URL. Use after a paper has been selected, not to discover papers (papers) or read an ordinary article URL (fetch). Ask for the identifier if it is missing.",
    "dedupe_sources": "Remove duplicate source items already provided by exact URL after trimming surrounding whitespace. Preserve the first item, metadata and order. Use an existing list only; not discovery, fetching, fuzzy matching or fact verification. Each item must have a nonblank string url. An empty list is valid; malformed items return an error, not fabricated replacements.",
}
parameter_descriptions = {
    "clarify": {"question": "One specific question requesting missing information or approval of content/destination.", "response_type": "text for missing facts; yes_no for external-action confirmation; choice for supplied options.", "options": "Only actual offered choices; empty for text or yes_no."},
    "timeline": {"screenname": "Canonical account handle without @. Not a human display name. Reuse the latest corrected account from context.", "limit": "Number of posts requested by the user; carry the latest corrected count. Default 5; integer 0 means no results."},
    "social_search": {"query": "The active subject/keywords, without adding abandoned topics or account guesses.", "search_type": "Latest for recent/current discussion; Top only when user explicitly asks popular/top. Use one mode unless both are requested.", "limit": "Requested number of posts; default 5; integer 0 means no results."},
    "lookup": {"query": "REQUIRED nonempty topic phrase from the user. Do not append news/today/this week when topic/timeframe already encode them; preserve the actual subject.", "topic": "news for current events/tin tuc; general for non-news information.", "timeframe": "day=today/24 hours; week=this week; month=this month; year=this year. Carry it from context until corrected.", "max_results": "Requested number of web results; default 5."},
    "fetch": {"url": "Exact active http(s) article URL supplied in the conversation; preserve path/query after corrections."},
    "format": {"items": "Actual existing source items, not invented search results.", "template": "Requested layout: brief, sections, bullets, thread or daily_ai_vn.", "headline": "Optional heading, not a new source claim."},
    "send": {"text": "Exact content the user approved for the configured destination.", "confirmed": "Boolean true only after explicit prior user confirmation of this specific action. Never infer consent."},
    "policy": {"query": "Question about internal company policy.", "policy_area": "Choose matching internal area, or all when unspecified.", "top_k": "Maximum policy excerpts; default 3, integer 0 means none."},
    "papers": {"query": "Scientific research topic to search on arXiv.", "max_results": "Maximum papers requested; default 5.", "sort_by": "relevance unless user asks latest update or submission date."},
    "paper_text": {"arxiv_url": "Provided arXiv ID or URL; never guess an identifier.", "max_pages": "Maximum PDF pages to read; default 5.", "max_chars": "Maximum extracted characters; default 8000."},
    "dedupe_sources": {"items": "Existing source list; each object requires nonblank string url. Keep original metadata; do not normalize paths, query strings, case or trailing slash."},
}
for tool in data["tools"]:
    name = tool["name"]
    tool["description"] = descriptions[name]
    for param, description in parameter_descriptions[name].items():
        tool["parameters"]["properties"][param]["description"] = description

# Only descriptions change: names, signatures, defaults and required fields are
# held constant to isolate the declaration-convention hypothesis.
(ROOT / "artifacts/tools.yaml").write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100), encoding="utf-8")
print("Rebuilt v3 tools.yaml: descriptions only; schema contract unchanged.")

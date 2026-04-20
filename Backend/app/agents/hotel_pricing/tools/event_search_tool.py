import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from duckduckgo_search import DDGS



class EventSearchToolInput(BaseModel):
    date_range: str = Field(
        ...,
        description="Date range to search events for, e.g. '2025-07-10 to 2025-07-15'"
    )


class EventSearchTool(BaseTool):
    name: str = "EventSearchTool"
    description: str = (
        "Searches for  major upcoming events in Antalya, Turkey for a given date range using DuckDuckGo."
       
        "Returns a list of events that may drive hotel demand."
    )
    args_schema: Type[BaseModel] = EventSearchToolInput

    def _run(self, date_range: str) -> str:
       
        # Build query and perform search, then filter results to prefer authoritative event sites
        query = f"Antalya events festivals activities {date_range}"
        raw_results = []

        # Domains we prefer for event information (whitelist substrings)
        whitelist = [
            'eventbrite.com', 'biletinial.com', 'biletiva.com', 'biletino.com', 'bubilet.com', 'bubilet.com.tr',
            'antalya.bel.tr', 'antalya.bozok', 'antalya.ktb', 'antalya-kultur',
            'festival', 'events', 'etkinlik', 'antalyakultur'
        ]
        # Domains to exclude (noise sources)
        blacklist = ['wikipedia.org', 'youtube.com', 'medium.com', 'tripadvisor.com']

        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=10):
                    # Keep raw dicts for filtering
                    raw_results.append(r)

            if not raw_results:
                return "No specific events found."

            # Prefer whitelist matches
            preferred = [r for r in raw_results if any(w in (r.get('href') or '').lower() for w in whitelist)]

            # Otherwise filter out known noisy domains
            if preferred:
                chosen = preferred[:5]
            else:
                filtered = [r for r in raw_results if not any(b in (r.get('href') or '').lower() for b in blacklist)]
                chosen = filtered[:5] if filtered else raw_results[:5]

            results = [f"Title: {r.get('title')}\nLink: {r.get('href')}\nSnippet: {r.get('body')}\n---" for r in chosen]

            return "\n".join(results) if results else "No specific events found."
        except Exception as e:
            return f"Search failed: {str(e)}"
                
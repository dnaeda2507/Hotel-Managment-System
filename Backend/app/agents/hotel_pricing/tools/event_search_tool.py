import os
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


class EventSearchToolInput(BaseModel):
    date_range: str = Field(
        ...,
        description="Date range to search events for, e.g. '2025-07-10 to 2025-07-15'"
    )


class EventSearchTool(BaseTool):
    name: str = "EventSearchTool"
    description: str = (
        "Searches for major upcoming events in Antalya, Turkey for a given date range using Brave Search. "
        "Returns a list of events that may drive hotel demand."
    )
    args_schema: Type[BaseModel] = EventSearchToolInput

    def _run(self, date_range: str) -> str:
        api_key = os.getenv("BRAVE_API_KEY", "")
        if not api_key:
            return "Brave API key not configured — skipping event search."

        query = f"Antalya etkinlik festival aktivite {date_range}"
        try:
            resp = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": api_key,
                },
                params={"q": query, "count": 10, "search_lang": "tr", "country": "TR"},
                timeout=15,
            )
            resp.raise_for_status()
            results = resp.json().get("web", {}).get("results", [])

            if not results:
                return "No specific events found."

            lines = []
            for r in results[:5]:
                lines.append(
                    f"Title: {r.get('title')}\n"
                    f"URL: {r.get('url')}\n"
                    f"Snippet: {r.get('description')}\n---"
                )
            return "\n".join(lines) if lines else "No specific events found."
        except Exception as e:
            return f"Search failed: {str(e)}"

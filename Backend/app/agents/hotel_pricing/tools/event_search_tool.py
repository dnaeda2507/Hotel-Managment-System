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
       
        query = f"Antalya events festivals activities {date_range}"
        results = []

        try:
            with DDGS() as ddgs:
                # Limit to 3 for speed and focus
                for r in ddgs.text(query, max_results=3):
                    results.append(f"Title: {r['title']}\nLink: {r['href']}\nSnippet: {r['body']}\n---")
            
            return "\n".join(results) if results else "No specific events found."
        except Exception as e:
            return f"Search failed: {str(e)}"
                
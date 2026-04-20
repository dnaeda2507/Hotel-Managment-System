import os
import yaml

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.weather_tool import WeatherTool
from .tools.event_search_tool import EventSearchTool
from .tools.occupancy_tool import OccupancyTool

@CrewBase
class HotelPricingCrew():
  
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    _db_session = None

    def set_db_session(self, db_session):
        """Inject DB session before calling kickoff."""
        self._db_session = db_session

    @agent
    def occupancy_analyst(self) -> Agent:
        occ_tool = OccupancyTool()
        occ_tool.db_session = self._db_session
        cfg = self.agents_config.get('occupancy_analyst', {})
        return Agent(
            config=cfg,
            tools=[occ_tool],
            verbose=True,
            allow_delegation=False,
        )

    @agent
    def market_researcher(self) -> Agent:
        cfg = self.agents_config.get('market_researcher', {})
        return Agent(
            config=cfg,
            tools=[EventSearchTool(), WeatherTool()],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def pricing_strategist(self) -> Agent:
        cfg = self.agents_config.get('pricing_strategist', {})
        return Agent(
            config=cfg,
            verbose=True,
            
            allow_delegation=False
        )

    @task
    def analyze_occupancy(self) -> Task:
        return Task(
            config=self.tasks_config.get('analyze_occupancy', {}),
            async_execution=True
        )

    @task
    def research_market(self) -> Task:
        return Task(
            config=self.tasks_config.get('research_market', {}),
            async_execution=True
        )


    @task
    def suggest_prices(self) -> Task:
        return Task(
            config=self.tasks_config.get('suggest_prices', {}),
            output_file='output/price_suggestions.json',
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

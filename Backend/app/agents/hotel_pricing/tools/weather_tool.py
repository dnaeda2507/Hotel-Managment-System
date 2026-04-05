import requests
from datetime import date
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


ANTALYA_LAT = 36.8969
ANTALYA_LON = 30.7133


class WeatherToolInput(BaseModel):
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")


class WeatherTool(BaseTool):
    name: str = "WeatherTool"
    description: str = (
        "Fetches weather forecast for Antalya, Turkey for a given date range. "
        "Returns daily max temperature and precipitation. "
        "Use this to understand if weather will attract or deter tourists."
    )
    args_schema: Type[BaseModel] = WeatherToolInput

    def _run(self, start_date: str, end_date: str) -> str:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": ANTALYA_LAT,
            "longitude": ANTALYA_LON,
            "daily": "temperature_2m_max,precipitation_sum",
            "timezone": "Europe/Istanbul",
            "start_date": start_date,
            "end_date": end_date,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            daily = data.get("daily", {})
            dates = daily.get("time", [])
            temps = daily.get("temperature_2m_max", [])
            precip = daily.get("precipitation_sum", [])

            if not dates:
                return "No weather data available for the given date range."

            lines = [f"Weather forecast for Antalya ({start_date} to {end_date}):"]
            total_temp = 0
            rainy_days = 0

            for i, d in enumerate(dates):
                t = temps[i] if i < len(temps) else "N/A"
                p = precip[i] if i < len(precip) else 0
                rain_note = " ☔ Rain expected" if p and p > 3 else ""
                lines.append(f"  {d}: Max {t}°C, Precipitation: {p}mm{rain_note}")
                if isinstance(t, (int, float)):
                    total_temp += t
                if isinstance(p, (int, float)) and p > 3:
                    rainy_days += 1

            avg_temp = total_temp / len(dates) if dates else 0
            lines.append(f"\nSummary: Avg max temp {avg_temp:.1f}°C, Rainy days: {rainy_days}/{len(dates)}")

            if avg_temp >= 28:
                lines.append("Assessment: Hot sunny weather — HIGH tourist appeal, supports premium pricing.")
            elif avg_temp >= 18:
                lines.append("Assessment: Pleasant weather — MODERATE tourist appeal.")
            else:
                lines.append("Assessment: Cool/cold weather — LOWER tourist demand expected.")

            return "\n".join(lines)

        except Exception as e:
            return f"Weather data unavailable: {str(e)}"

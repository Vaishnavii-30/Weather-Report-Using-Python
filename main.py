from fastapi import FastAPI, HTTPException, Query
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

# load environment variables
load_dotenv()
API_KEY = os.getenv("364ffe3ce002496895762104250509")
if not API_KEY:
    raise RuntimeError("364ffe3ce002496895762104250509")

# ✅ this must exist
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# requests session with retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.4, status_forcelist=[429,500,502,503,504])
session.mount("https://", HTTPAdapter(max_retries=retries))


class WeatherOut(BaseModel):
    city: str
    temp_c: float
    description: str
    humidity: int
    wind_speed: float

@app.get("/api/weather", response_model=WeatherOut)
def get_weather(city: str = Query(..., min_length=2)):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        r = session.get(url, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        main = data.get("main") or {}
        weather = data.get("weather") or [{}]
        return WeatherOut(
            city = data.get("name", city),
            temp_c = main.get("temp", 0.0),
            description = weather[0].get("description",""),
            humidity = main.get("humidity",0),
            wind_speed = data.get("wind",{}).get("speed",0.0)
        )
    except requests.HTTPError as ex:
        # map external errors to client-friendly errors
        code = ex.response.status_code if ex.response is not None else 502
        detail = ex.response.json().get("message", "External API error") if ex.response is not None else str(ex)
        raise HTTPException(status_code=code, detail=detail)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.get("/api/forecast")
def get_forecast(lat: float, lon: float):
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
    try:
        r = session.get(url, params=params, timeout=6)
        r.raise_for_status()
        data = r.json()
        # reduce to list of {dt_txt, temp}
        entries = []
        for item in data.get("list", [])[:12]:  # first 12 timestamps (~36 hours)
            entries.append({"time": item.get("dt_txt"), "temp": item.get("main",{}).get("temp")})
        return {"city": data.get("city",{}).get("name"), "items": entries}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
@app.get("/")
def read_root():
    return {"message": "Weather API is running!"}

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATION_API_KEY")

URL = "https://api.aviationstack.com/v1/flights"


def search_flights(origin, destination=None):

    params = {
        "access_key": API_KEY,
        "dep_iata": origin,
        "limit": 10
    }

    if destination:
        params["arr_iata"] = destination

    response = requests.get(
        URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise Exception(data["error"])

    return data.get("data", [])
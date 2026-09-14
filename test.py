import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAILRADAR_API_KEY = os.getenv("RAILRADAR_API_KEY")

RAILRADAR_URL = "https://api.railradar.in/v1/trains/between"


def search_train(from_station, to_station, travel_date):

    url = f"{RAILRADAR_URL}/{from_station}/{to_station}"

    headers = {
        "Authorization": f"Bearer {RAILRADAR_API_KEY}",
        "Accept": "application/json"
    }

    params = {
        "date": travel_date
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20
    )

    print("Request URL:", response.url)
    print("Status:", response.status_code)
    print(response.text)

    return response
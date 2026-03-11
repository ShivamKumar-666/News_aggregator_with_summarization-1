import requests
import os
from dotenv import load_dotenv

load_dotenv()

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

def fetch_news(category="general", max_articles=10):
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        "category": category,
        "lang": "en",
        "country": "us",
        "max": max_articles,
        "apikey": GNEWS_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    return []
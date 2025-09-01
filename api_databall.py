import requests
from config import API_KEY

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

def get_fixtures_by_date(start_date, end_date, competition_code):
    url = f"{BASE_URL}/competitions/{competition_code}/matches?dateFrom={start_date}&dateTo={end_date}"
    print(f"🌐 Requesting URL: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 200:
        return resp.json().get("matches", [])
    print(f"❌ Error fetching fixtures for {competition_code}: {resp.status_code} {resp.text[:200]}")
    return []

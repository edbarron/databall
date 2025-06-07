import requests
from config import API_KEY

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {
    "X-Auth-Token": API_KEY
}

# Get fixtures by date and competition code (e.g., PL, CL, SA)
def get_fixtures_by_date(start_date, end_date, competition_code):
    url = f"{BASE_URL}/competitions/{competition_code}/matches?dateFrom={start_date}&dateTo={end_date}"
    print(f"🌐 Requesting URL: {url}")
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("matches", [])
    else:
        print(f"❌ Error fetching fixtures for {competition_code}: {response.status_code}")
        return []

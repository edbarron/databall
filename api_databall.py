import requests
from config import API_KEY

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY
}

# Get all available leagues
def get_leagues():
    url = f"{BASE_URL}/leagues"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        print("Error fetching leagues:", response.status_code)
        return []

# Get all teams for a league and season
def get_teams(league_id, season):
    url = f"{BASE_URL}/teams?league={league_id}&season={season}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        print("Error fetching teams:", response.status_code)
        return []

def get_fixtures_by_date(start_date, end_date, league_id=None):
    url = f"{BASE_URL}/fixtures?from={start_date}&to={end_date}"
    if league_id:
        url += f"&league={league_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        print(f"Error fetching fixtures for league {league_id}: {response.status_code}")
        return []


# Get match statistics
def get_match_statistics(fixture_id):
    url = f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("response", [])
    else:
        print("Error fetching statistics:", response.status_code)
        return []

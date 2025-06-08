from db_utils import get_last_matches_for_team, query_matches_by_date
from tabulate import tabulate
from utils import get_date_range
import datetime

def simulate_by_day():
    print("\n📆 Choose a day to simulate:")
    print("1. Today")
    print("2. Tomorrow")
    print("3. Custom")

    option = input("\n👉 Option (1-3): ")
    today = datetime.date.today()

    if option == "1":
        date = today.strftime("%Y-%m-%d")
    elif option == "2":
        date = (today + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    elif option == "3":
        date = input("📅 Enter date (YYYY-MM-DD): ")
    else:
        print("❌ Invalid option.")
        return

    matches = query_matches_by_date(date)

    if not matches:
        print("⚠️ No matches found for that date.")
        return

    predictions = []

    for match in matches:
        home_id = match["home_team_id"]
        away_id = match["away_team_id"]
        home_name = match["home_team"]
        away_name = match["away_team"]

        recent_home = get_last_matches_for_team(home_id, 5)
        recent_away = get_last_matches_for_team(away_id, 5)

        home_wins = sum(1 for m in recent_home if m["result"] == "home_win")
        away_wins = sum(1 for m in recent_away if m["result"] == "away_win")

        total = home_wins + away_wins or 1
        home_prob = round((home_wins / total) * 100)
        away_prob = 100 - home_prob

        predictions.append({
            "Date": match["date"],
            "Match": f"{home_name} vs {away_name}",
            "Prediction": f"{home_name if home_prob > away_prob else away_name}",
            "Confidence": f"{max(home_prob, away_prob)}%",
            "Expected Goals": "2-3"
        })

    print(tabulate(predictions, headers="keys", tablefmt="fancy_grid"))

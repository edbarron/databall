# simulate.py
from db_utils import get_last_matches_for_team, query_matches_by_date
from tabulate import tabulate
import datetime

def _team_win_count(recent, team_id):
    wins = 0
    for m in recent:
        if m["home_goals"] is None or m["away_goals"] is None:
            continue
        if m["home_team_id"] == team_id and m["home_goals"] > m["away_goals"]:
            wins += 1
        if m["away_team_id"] == team_id and m["away_goals"] > m["home_goals"]:
            wins += 1
    return wins

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
        home_id, away_id = match["home_team_id"], match["away_team_id"]
        home_name, away_name = match["home_team"], match["away_team"]

        recent_home = get_last_matches_for_team(home_id, 5)
        recent_away = get_last_matches_for_team(away_id, 5)

        home_wins = _team_win_count(recent_home, home_id)
        away_wins = _team_win_count(recent_away, away_id)
        total = max(home_wins + away_wins, 1)

        home_prob = round((home_wins / total) * 100)
        away_prob = 100 - home_prob

        # expected goals (simple robust means)
        def _goals_as(team_id, matches):
            goals = []
            for m in matches:
                hg, ag = m["home_goals"], m["away_goals"]
                if hg is None or ag is None:
                    continue
                goals.append(hg if m["home_team_id"] == team_id else ag)
            return goals

        hg = _goals_as(home_id, recent_home)
        ag = _goals_as(away_id, recent_away)
        avg_home_goals = round(sum(hg)/len(hg), 1) if hg else 1.0
        avg_away_goals = round(sum(ag)/len(ag), 1) if ag else 1.0

        predicted = home_name if home_prob >= away_prob else away_name
        predictions.append({
            "Date": match["date"],
            "Match": f"{home_name} vs {away_name}",
            "Prediction": predicted,
            "Confidence": f"{max(home_prob, away_prob)}%",
            "Expected Goals": f"{avg_home_goals} - {avg_away_goals}",
        })
    print(tabulate(predictions, headers="keys", tablefmt="fancy_grid"))

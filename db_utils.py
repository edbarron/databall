import sqlite3
from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


# Insert a tournament
def insert_tournament(id, name, type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO tournaments (id, name, type)
        VALUES (?, ?, ?)
    """, (id, name, type))
    conn.commit()
    conn.close()


# Insert a league
def insert_league(id, name, country, season, tournament_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO leagues (id, name, country, season, tournament_id)
        VALUES (?, ?, ?, ?, ?)
    """, (id, name, country, season, tournament_id))
    conn.commit()
    conn.close()


# Insert a team
def insert_team(id, name, league_id, country, is_national_team=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO teams (id, name, league_id, country, is_national_team)
        VALUES (?, ?, ?, ?, ?)
    """, (id, name, league_id, country, int(is_national_team)))
    conn.commit()
    conn.close()


# Insert a match (from fixture object)
def insert_match(fixture):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        match_id = fixture["fixture"]["id"]
        date = fixture["fixture"]["date"][:10]
        league_id = fixture["league"]["id"]
        home_team_id = fixture["teams"]["home"]["id"]
        away_team_id = fixture["teams"]["away"]["id"]
        home_goals = fixture["goals"]["home"]
        away_goals = fixture["goals"]["away"]

        if home_goals is None or away_goals is None:
            result = "pending"
        elif home_goals > away_goals:
            result = "home_win"
        elif home_goals < away_goals:
            result = "away_win"
        else:
            result = "draw"

        cursor.execute("""
            INSERT OR IGNORE INTO matches (id, date, league_id, home_team_id, away_team_id, home_goals, away_goals, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (match_id, date, league_id, home_team_id, away_team_id, home_goals, away_goals, result))

        conn.commit()
        return match_id
    except Exception as e:
        print(f"❌ Error inserting match: {e}")
        return None
    finally:
        conn.close()


# Insert match statistics
def insert_match_statistics(match_id, stats):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO match_statistics (
            match_id, possession_home, possession_away, shots_home, shots_away,
            corners_home, corners_away, free_kicks_home, free_kicks_away,
            penalties_home, penalties_away, fouls_home, fouls_away,
            yellow_cards_home, yellow_cards_away, red_cards_home, red_cards_away
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        match_id,
        stats.get("possession_home"), stats.get("possession_away"),
        stats.get("shots_home"), stats.get("shots_away"),
        stats.get("corners_home"), stats.get("corners_away"),
        stats.get("free_kicks_home"), stats.get("free_kicks_away"),
        stats.get("penalties_home"), stats.get("penalties_away"),
        stats.get("fouls_home"), stats.get("fouls_away"),
        stats.get("yellow_cards_home"), stats.get("yellow_cards_away"),
        stats.get("red_cards_home"), stats.get("red_cards_away")
    ))
    conn.commit()
    conn.close()


# Query stored matches
def query_stored_matches():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.id, m.date, l.name as league, th.name as home_team,
               ta.name as away_team, m.home_goals, m.away_goals, m.result
        FROM matches m
        JOIN leagues l ON m.league_id = l.id
        JOIN teams th ON m.home_team_id = th.id
        JOIN teams ta ON m.away_team_id = ta.id
        ORDER BY m.date DESC
    """)
    rows = cursor.fetchall()
    colnames = [description[0] for description in cursor.description]
    conn.close()
    return [dict(zip(colnames, row)) for row in rows]


# Export matches to Excel
def export_matches_to_excel(filename):
    try:
        import pandas as pd
        data = query_stored_matches()
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        return True
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

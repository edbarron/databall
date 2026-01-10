# db_utils.py
import sqlite3
from config import DB_PATH

# ----------------------------
# Connection helper
# ----------------------------
def get_connection():
    """
    Opens a SQLite connection with foreign keys enabled and dict-like rows.
    Use with: `with get_connection() as conn: ...`
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------------
# Inserts / Upserts
# ----------------------------
def insert_league(id, name, country, season):
    """
    Upsert de liga por PRIMARY KEY (id).
    """
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO leagues (id, name, country, season)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                country = excluded.country,
                season = excluded.season
            """,
            (id, name, country, season),
        )

def insert_team(id, name, league_id, country, is_national_team=False):
    """
    Upsert de equipo por PRIMARY KEY (id).
    """
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO teams (id, name, league_id, country)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                league_id = excluded.league_id,
                country = excluded.country
            """,
            (id, name, league_id, country),
        )

def insert_match(fixture):
    """
    Upsert de match: actualiza si existe.
    - No sobreescribe goles con NULL si ya hay marcador.
    - Cuando hay marcador final, lo actualiza.
    """
    try:
        match_id = fixture["id"]
        date = fixture["utcDate"][:10]  # 'YYYY-MM-DD'

        league = fixture["competition"]
        league_id = league["id"]
        league_name = league["name"]
        country = fixture["area"]["name"]
        season = (fixture.get("season", {}).get("startDate", "unknown") or "unknown")[:4]

        home_team = fixture["homeTeam"]
        away_team = fixture["awayTeam"]

        score = fixture.get("score", {})
        full_time = score.get("fullTime", {})
        home_goals = full_time.get("home")
        away_goals = full_time.get("away")

        if home_goals is None or away_goals is None:
            result = "pending"
        elif home_goals > away_goals:
            result = "home_win"
        elif home_goals < away_goals:
            result = "away_win"
        else:
            result = "draw"

        with get_connection() as conn:
            # UPSERT liga
            conn.execute(
                """
                INSERT INTO leagues (id, name, country, season)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    country = excluded.country,
                    season = excluded.season
                """,
                (league_id, league_name, country, season),
            )

            # UPSERT equipos
            conn.execute(
                """
                INSERT INTO teams (id, name, league_id, country)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    league_id = excluded.league_id,
                    country = excluded.country
                """,
                (home_team["id"], home_team["name"], league_id, country),
            )
            conn.execute(
                """
                INSERT INTO teams (id, name, league_id, country)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    league_id = excluded.league_id,
                    country = excluded.country
                """,
                (away_team["id"], away_team["name"], league_id, country),
            )

            # UPSERT partido
            # - Si el nuevo fixture no trae marcador (NULL), conservamos el existente.
            # - Si trae marcador final, actualizamos goles y resultado.
            conn.execute(
                """
                INSERT INTO matches (
                    id, date, league_id, home_team_id, away_team_id,
                    home_goals, away_goals, result
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    date         = excluded.date,
                    league_id    = excluded.league_id,
                    home_team_id = excluded.home_team_id,
                    away_team_id = excluded.away_team_id,
                    home_goals   = COALESCE(excluded.home_goals, matches.home_goals),
                    away_goals   = COALESCE(excluded.away_goals, matches.away_goals),
                    result       = CASE
                        WHEN excluded.result IS NOT NULL AND excluded.result <> 'pending'
                            THEN excluded.result
                        ELSE matches.result
                    END
                """,
                (
                    match_id,
                    date,
                    league_id,
                    home_team["id"],
                    away_team["id"],
                    home_goals,
                    away_goals,
                    result,
                ),
            )

        return match_id
    except Exception as e:
        print(f"❌ Error inserting match ID {fixture.get('id')}: {e}")
        return None

def insert_match_statistics(match_id, stats):
    """
    Optional: requires match_statistics table present in schema.
    """
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO match_statistics (
                match_id, possession_home, possession_away, shots_home, shots_away,
                corners_home, corners_away, free_kicks_home, free_kicks_away,
                penalties_home, penalties_away, fouls_home, fouls_away,
                yellow_cards_home, yellow_cards_away, red_cards_home, red_cards_away
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id,
                stats.get("possession_home"),
                stats.get("possession_away"),
                stats.get("shots_home"),
                stats.get("shots_away"),
                stats.get("corners_home"),
                stats.get("corners_away"),
                stats.get("free_kicks_home"),
                stats.get("free_kicks_away"),
                stats.get("penalties_home"),
                stats.get("penalties_away"),
                stats.get("fouls_home"),
                stats.get("fouls_away"),
                stats.get("yellow_cards_home"),
                stats.get("yellow_cards_away"),
                stats.get("red_cards_home"),
                stats.get("red_cards_away"),
            ),
        )

# ----------------------------
# Queries / Exports
# ----------------------------
def _rows_to_dicts(rows):
    return [dict(r) for r in rows]

def query_stored_matches(start_date, end_date):
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT
                m.id,
                m.date,
                l.name AS league,
                th.name AS home_team,
                ta.name AS away_team,
                m.home_goals,
                m.away_goals,
                m.result
            FROM matches m
            JOIN leagues l ON m.league_id = l.id
            JOIN teams   th ON m.home_team_id = th.id
            JOIN teams   ta ON m.away_team_id = ta.id
            WHERE m.date BETWEEN ? AND ?
            ORDER BY m.date DESC
            """,
            (start_date, end_date),
        )
        return _rows_to_dicts(cur.fetchall())

def get_last_matches_for_team(team_id, limit=5):
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT *
            FROM matches
            WHERE home_team_id = ? OR away_team_id = ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (team_id, team_id, limit),
        )
        return _rows_to_dicts(cur.fetchall())

def query_matches_by_date(date):
    """
    Returns matches for a given date with ids/names and league_id,
    useful for predictors/simulations.
    """
    with get_connection() as conn:
        cur = conn.execute(
            """
            SELECT
                m.id,
                m.date,
                m.league_id,
                l.name AS league,
                th.name AS home_team,
                ta.name AS away_team,
                m.home_team_id,
                m.away_team_id,
                m.result,
                m.home_goals,
                m.away_goals
            FROM matches m
            JOIN leagues l ON m.league_id = l.id
            JOIN teams   th ON m.home_team_id = th.id
            JOIN teams   ta ON m.away_team_id = ta.id
            WHERE m.date = ?
            ORDER BY m.date DESC
            """,
            (date,),
        )
        return _rows_to_dicts(cur.fetchall())

def export_matches_to_excel(filename, start_date, end_date):
    """
    Export matches in [start_date, end_date] to an .xlsx file.
    Returns True on success, False otherwise.
    """
    try:
        import pandas as pd
        from pathlib import Path

        data = query_stored_matches(start_date, end_date)
        if not data:
            print("⚠️ No matches found in the selected range.")
            return False

        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        return True

    except ImportError:
        print("❌ Export failed: pandas (and openpyxl) are required. Install with:")
        print("   pip install pandas openpyxl")
        return False
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False

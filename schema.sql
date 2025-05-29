-- schema.sql – Base structure for Databall database

-- Leagues table
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT,
    season TEXT NOT NULL
);

-- Teams table
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    league_id INTEGER NOT NULL,
    country TEXT,
    FOREIGN KEY (league_id) REFERENCES leagues(id)
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    date DATETIME NOT NULL,
    league_id INTEGER NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_goals INTEGER,
    away_goals INTEGER,
    result TEXT,
    FOREIGN KEY (league_id) REFERENCES leagues(id),
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id)
);

-- Match statistics table
CREATE TABLE IF NOT EXISTS match_statistics (
    id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    possession_home INTEGER,
    possession_away INTEGER,
    shots_home INTEGER,
    shots_away INTEGER,
    corners_home INTEGER,
    corners_away INTEGER,
    free_kicks_home INTEGER,
    free_kicks_away INTEGER,
    penalties_home INTEGER,
    penalties_away INTEGER,
    fouls_home INTEGER,
    fouls_away INTEGER,
    yellow_cards_home INTEGER,
    yellow_cards_away INTEGER,
    red_cards_home INTEGER,
    red_cards_away INTEGER,
    FOREIGN KEY (match_id) REFERENCES matches(id)
);

-- Players table
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    team_id INTEGER NOT NULL,
    position TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Player statistics per match
CREATE TABLE IF NOT EXISTS player_statistics (
    id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,
    match_id INTEGER NOT NULL,
    goals INTEGER DEFAULT 0,
    assists INTEGER DEFAULT 0,
    minutes_played INTEGER DEFAULT 0,
    penalties_scored INTEGER DEFAULT 0,
    yellow_cards INTEGER DEFAULT 0,
    red_cards INTEGER DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(id),
    FOREIGN KEY (match_id) REFERENCES matches(id)
);



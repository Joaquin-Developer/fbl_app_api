create database sa_cup_24;
use sa_cup_24;

CREATE TABLE teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    home_team_score INTEGER DEFAULT 0,
    away_team_score INTEGER DEFAULT 0,
    played BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id)
);

CREATE TABLE statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INTEGER UNIQUE NOT NULL,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    gf INTEGER DEFAULT 0,
    ga INTEGER DEFAULT 0,
    pts INTEGER DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES teams(id)
);


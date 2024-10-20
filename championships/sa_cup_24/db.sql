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

CREATE VIEW team_statistics AS
WITH dynamic_statistics AS (
    SELECT 
        t.id AS team_id,
        t.name AS team_name,
        COUNT(m.id) AS matches_played,
        SUM(
            CASE 
                WHEN m.home_team_id = t.id AND m.home_team_score > m.away_team_score THEN 1
                WHEN m.away_team_id = t.id AND m.away_team_score > m.home_team_score THEN 1
                ELSE 0 
            END
        ) AS wins,
        SUM(
            CASE 
                WHEN m.home_team_id = t.id AND m.home_team_score < m.away_team_score THEN 1
                WHEN m.away_team_id = t.id AND m.away_team_score < m.home_team_score THEN 1
                ELSE 0 
            END
        ) AS losses,
        SUM(
            CASE 
                WHEN m.home_team_score = m.away_team_score THEN 1
                ELSE 0 
            END
        ) AS draws,
        SUM(
            CASE 
                WHEN m.home_team_id = t.id THEN m.home_team_score
                ELSE m.away_team_score
            END
        ) AS gf, -- Goals For
        SUM(
            CASE 
                WHEN m.home_team_id = t.id THEN m.away_team_score
                ELSE m.home_team_score
            END
        ) AS ga, -- Goals Against
        (SUM(
            CASE 
                WHEN m.home_team_id = t.id AND m.home_team_score > m.away_team_score THEN 3
                WHEN m.away_team_id = t.id AND m.away_team_score > m.home_team_score THEN 3
                WHEN m.home_team_score = m.away_team_score THEN 1
                ELSE 0 
            END
        )) AS pts -- Points
    FROM 
        teams t
    LEFT JOIN 
        matches m 
        ON t.id = m.home_team_id OR t.id = m.away_team_id
    WHERE 
        m.played = TRUE
    GROUP BY 
        t.id, t.name
)
SELECT
    team_id, team_name, matches_played as TP,
    wins as WP,
    losses as LP,
    draws as DP,
    gf as GF,
    ga as GA,
    (gf - ga) as DIFF,
    pts as PTS
FROM dynamic_statistics
ORDER BY 9 DESC, 8 DESC;

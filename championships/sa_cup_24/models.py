from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Modelos de entrada y salida para Team
class TeamBase(BaseModel):
    name: str
    city: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int

    class Config:
        orm_mode = True


# Modelos de entrada y salida para Match
class MatchBase(BaseModel):
    home_team_id: int
    away_team_id: int
    round: int
    date: Optional[datetime] = None


class MatchCreate(MatchBase):
    pass


class MatchResult(BaseModel):
    id: int
    home_team_score: int
    away_team_score: int


class MatchResponse(MatchBase):
    id: int
    round: int
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    home_team_score: int
    away_team_score: int

    class Config:
        orm_mode = True


# Modelos de entrada y salida para Statistics
class StatisticsBase(BaseModel):
    matches_played: int
    wins: int
    losses: int
    draws: int
    goals_for: int
    goals_against: int
    points: int


class StatisticsResponse(StatisticsBase):
    id: int
    team_id: int

    class Config:
        orm_mode = True

class TeamStatisticsResponse(BaseModel):
    team_id: int
    team_name: str
    TP: int
    WP: int
    LP: int
    DP: int
    GF: int  # Goals For
    GA: int  # Goals Against
    DIFF: int  # GF - GA
    PTS: int  # Points

    class Config:
        orm_mode = True

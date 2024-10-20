import logging
from typing import List

from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, aliased, Query

from championships.sa_cup_24.database import get_db
from championships.sa_cup_24.schemas import Team, Match, Statistics
from championships.sa_cup_24.models import MatchResponse


logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/")
def main():
    return Response(content="Hello World!", status_code=200)


@router.get("/generate_matches")
def generate_matches(db: Session = Depends(get_db)):
    """
    Create all matches for date, if no matches have been created yet.
    """
    len_actual_matches = db.query(Match).count()

    if len_actual_matches > 0:
        return Response({"detail": "Matches are already created.", "total_matches": len_actual_matches})

    teams = db.query(Team).all()
    len_teams = len(teams)

    if len_teams <= 2:
        raise HTTPException(status_code=400, detail="FATAL: Missing teams")

    matches: List[Match] = []
    round_number = 1

    for _ in range(len_teams - 1):
        for j in range(len_teams // 2):
            home_team = teams[j]
            away_team = teams[len_teams - 1 - j]

            matches.append(
                Match(
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    round=round_number,
                )
            )
        teams.insert(1, teams.pop())
        round_number += 1

    try:
        db.bulk_save_objects(matches)
        db.commit()
        return JSONResponse({"detail": "OK", "total_matches": len(matches)})
    except Exception as error:
        logging.error(str(error))
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal error.")


def all_matches(db: Session) -> Query:
    """
    Get all matches
    """
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)

    return db.query(
        Match.id,
        Match.round,
        Match.home_team_id,
        HomeTeam.name.label("home_team_name"),
        Match.away_team_id,
        AwayTeam.name.label("away_team_name"),
        Match.home_team_score,
        Match.away_team_score
    ).join(HomeTeam, Match.home_team_id == HomeTeam.id) \
        .join(AwayTeam, Match.away_team_id == AwayTeam.id) \


@router.get("/get_all_matches", response_model=List[MatchResponse])
def get_all_matches(db: Session = Depends(get_db)):
    """
    Return all matches.
    """
    return all_matches(db).order_by(Match.round.asc(), Match.id.asc()).all()


@router.get("/get_matches_last_date", response_model=List[MatchResponse])
def get_matches_last_date(db: Session = Depends(get_db)):
    """
    Return all matches for the last date.
    """
    last_round = db.query(Match.round).filter(Match.played == True).order_by(Match.round.desc()).first()

    if not last_round:
        return []

    _all_matches = all_matches(db).filter(Match.round == last_round[0], Match.played == True)
    return _all_matches.order_by(Match.round.asc(), Match.id.asc()).all()


@router.get("/statistics")
def statistics(db: Session = Depends(get_db)):
    """
    Return all statistics
    """
    db.query(Statistics).all()

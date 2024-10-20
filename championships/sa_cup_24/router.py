import logging
from typing import List

from fastapi import APIRouter, Response, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from championships.sa_cup_24.database import get_db
from championships.sa_cup_24.schemas import Team, Match #, Statistics
from championships.sa_cup_24.models import MatchResponse, MatchResult, TeamStatisticsResponse
from championships.sa_cup_24.logic.statistics import update_statistics, get_statistics, generate_image
from championships.sa_cup_24.logic.matches import all_matches
import utils


logging.basicConfig(level=logging.INFO)

router = APIRouter()


@router.get("/")
def main():
    return Response(content="Hello World!")


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


@router.post("/update_match")
def update_match(result: MatchResult, db: Session = Depends(get_db)):
    """
    Update the result of a match and adjust statistics.
    """
    match_obj = db.query(Match).filter(Match.id == result.id).first()

    if not match_obj:
        raise HTTPException(status_code=404, detail="Match not found")

    match_obj.home_team_score = result.home_team_score
    match_obj.away_team_score = result.away_team_score
    match_obj.played = True

    try:
        update_statistics(match_obj, db)
        db.commit()

        return JSONResponse(
            {"message": "Match result updated and statistics adjusted"}
        )
    except Exception as error:
        logging.error(str(error))
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal error.")


# @router.get("/statistics", response_model=List[TeamStatisticsResponse])
# def statistics(db: Session = Depends(get_db)):
#     """
#     Return all statistics
#     """
#     db.query(Statistics).all()


@router.get("/statistics", response_model=List[TeamStatisticsResponse])
def statistics(db: Session = Depends(get_db)):
    """
    Return all statistics
    """
    return get_statistics(db)


@router.get("/statistics_img", response_class=StreamingResponse)
def statistics_img(language: str = utils.Language.EN, db: Session = Depends(get_db)):
    return generate_image(db=db, language=language)

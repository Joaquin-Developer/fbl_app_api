from sqlalchemy.orm import Session, aliased, Query

from championships.sa_cup_24.schemas import Team, Match


def all_matches(db: Session) -> Query:
    """
    Get all matches
    """
    HomeTeam = aliased(Team)
    AwayTeam = aliased(Team)

    return (
        db.query(
            Match.id,
            Match.round,
            Match.home_team_id,
            HomeTeam.name.label("home_team_name"),
            Match.away_team_id,
            AwayTeam.name.label("away_team_name"),
            Match.home_team_score,
            Match.away_team_score,
            Match.played
        )
        .join(HomeTeam, Match.home_team_id == HomeTeam.id)
        .join(AwayTeam, Match.away_team_id == AwayTeam.id)
    )

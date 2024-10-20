from typing import List
from io import BytesIO

from sqlalchemy.orm import Session
from sqlalchemy import text
import matplotlib.pyplot as plt
import pandas as pd
from fastapi.responses import StreamingResponse

from championships.sa_cup_24.schemas import Match, Team, Statistics
from championships.sa_cup_24.models import TeamStatisticsResponse
from utils import Language


TRANSLATIONS = {
    Language.ES: {
        "Team Name": "Equipo",
        "Matches Played": "PJ",
        "Wins": "PG",
        "Losses": "PP",
        "Draws": "PE",
        "Goals For": "GF",
        "Goals Against": "GC",
        "Goal Difference": "DG",
        "Points": "Puntos",
    },
    Language.EN: {
        "Team Name": "Team",
        "Matches Played": "TP",
        "Wins": "Wins",
        "Losses": "Losses",
        "Draws": "Draws",
        "Goals For": "Goals For",
        "Goals Against": "Goals Against",
        "Goal Difference": "Goal Diff",
        "Points": "Points",
    },
}


def create_statistics_object(team_id: int) -> Statistics:
    """
    Create and returns default Statistics object
    """
    return Statistics(
        team_id=team_id,
        matches_played=0,
        wins=0,
        losses=0,
        draws=0,
        gf=0,
        ga=0,
        pts=0
    )


def update_statistics(match_obj: Match, db: Session):
    """
    Update statistics for both teams based on the result of a match_obj.
    """
    # Get teams
    home_team = db.query(Team).filter(Team.id == match_obj.home_team_id).first()
    away_team = db.query(Team).filter(Team.id == match_obj.away_team_id).first()

    # Get or create statistics for both teams
    home_stats = db.query(Statistics).filter(Statistics.team_id == home_team.id).first()
    away_stats = db.query(Statistics).filter(Statistics.team_id == away_team.id).first()

    # create statistics if not exists from local team
    if not home_stats:
        home_stats = create_statistics_object(home_team.id)
        db.add(home_stats)

    # create statistics if not exists from away team
    if not away_stats:
        away_stats = create_statistics_object(away_team.id)
        db.add(away_stats)

    # Update statistics based on results
    home_stats.matches_played += 1
    away_stats.matches_played += 1

    home_stats.gf += match_obj.home_team_score
    home_stats.ga += match_obj.away_team_score
    away_stats.gf += match_obj.away_team_score
    away_stats.ga += match_obj.home_team_score

    if match_obj.home_team_score > match_obj.away_team_score:
        # Home team wins
        home_stats.wins += 1
        home_stats.pts += 3
        away_stats.losses += 1
    elif match_obj.home_team_score < match_obj.away_team_score:
        # Away team wins
        away_stats.wins += 1
        away_stats.pts += 3
        home_stats.losses += 1
    else:
        # Draw
        home_stats.draws += 1
        away_stats.draws += 1
        home_stats.pts += 1
        away_stats.pts += 1

    db.commit()


def get_statistics(db: Session) -> List[TeamStatisticsResponse]:
    sql_query = """
        SELECT team_id, team_name, TP, WP, LP, DP, GF, GA, DIFF, PTS
        FROM team_statistics
    """
    results = db.execute(text(sql_query)).mappings().all()
    return [
        TeamStatisticsResponse(
            team_id=row["team_id"],
            team_name=row["team_name"],
            TP=row["TP"],
            WP=row["WP"],
            LP=row["LP"],
            DP=row["DP"],
            GF=row["GF"],
            GA=row["GA"],
            DIFF=row["DIFF"],
            PTS=row["PTS"],
        )
        for row in results
    ]


def generate_image(
    db: Session, language: Language = Language.EN, data: List[TeamStatisticsResponse] = None
) -> StreamingResponse:
    """
    Generate an image of a table from the given team statistics data.
    
    Parameters:
    - data: List of TeamStatisticsResponse objects.
    
    Returns:
    - A StreamingResponse containing the image of the table.
    """
    if not data:
        data = get_statistics(db)

    labels = TRANSLATIONS.get(language)

    df = pd.DataFrame([{
        labels["Team Name"]: row.team_name,
        labels["Matches Played"]: row.TP,
        labels["Wins"]: row.WP,
        labels["Losses"]: row.LP,
        labels["Draws"]: row.DP,
        labels["Goals For"]: row.GF,
        labels["Goals Against"]: row.GA,
        labels["Goal Difference"]: row.DIFF,
        labels["Points"]: row.PTS,
    } for row in data])

    # Create a matplotlib figure and axis
    fig, ax = plt.subplots(figsize=(12, len(df) * 0.5))  # Adjust the size as needed
    ax.axis("tight")
    ax.axis("off")

    # Create the table
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc="center", loc="center")

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.5, 1.5)  # Adjust cell size

    # Set specific column widths if needed
    for i in range(len(df.columns)):
        # Automatically adjust column width based on content
        table.auto_set_column_width(i)

    # Save the figure to a BytesIO object
    buf = BytesIO()
    # plt.savefig(buf, format="png", bbox_inches="tight")
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)  # Higher DPI for better quality
    buf.seek(0)

    plt.close(fig)

    return StreamingResponse(buf, media_type="image/png")

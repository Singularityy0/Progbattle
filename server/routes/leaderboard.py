from flask import Blueprint, jsonify
from models.models import Team, Submission
from models.database import db
from sqlalchemy import func

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")

@leaderboard_bp.route("/round/<int:round_num>")
def round_leaderboard(round_num):
    if round_num not in [1, 2]:
        return jsonify({"error": "Invalid round number"}), 400

    results = (
        db.session.query(
            Team.id,
            Team.name,
            func.sum(Submission.score).label("total_score"),
            func.count(Submission.id).label("matches_played")
        )
        .join(Submission, Submission.team_id == Team.id)
        .filter(Team.round == round_num)
        .group_by(Team.id, Team.name)
        .order_by(func.sum(Submission.score).desc())
        .all()
    )

    leaderboard_data = [{
        "team_id": team_id,
        "team_name": team_name,
        "total_score": total_score,
        "matches_played": matches_played
    } for team_id, team_name, total_score, matches_played in results]

    return jsonify(leaderboard_data)

@leaderboard_bp.route("/qualify-round-2", methods=["POST"])
def qualify_round_2():
    # Get top 16 teams from round 1
    top_teams = (
        db.session.query(
            Team.id,
            func.sum(Submission.score).label("total_score")
        )
        .join(Submission, Submission.team_id == Team.id)
        .filter(Team.round == 1)
        .group_by(Team.id)
        .order_by(func.sum(Submission.score).desc())
        .limit(16)
        .all()
    )

    # Update their round to 2
    for team_id, _ in top_teams:
        team = Team.query.get(team_id)
        team.round = 2

    db.session.commit()

    return jsonify({
        "message": "Top 16 teams advanced to round 2",
        "qualified_teams": [team_id for team_id, _ in top_teams]
    })

@leaderboard_bp.route("/")
def leaderboard():
    results = (
        db.session.query(Team.name, func.sum(Submission.score).label("total_score"))
        .join(Submission, Submission.team_id == Team.id)
        .group_by(Team.name)
        .order_by(func.sum(Submission.score).desc())
        .all()
    )

    leaderboard_data = [
        {"team": team_name, "score": score} for team_name, score in results
    ]

    return jsonify(leaderboard_data)

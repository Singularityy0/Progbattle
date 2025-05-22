from flask import Blueprint, jsonify
from models.models import Team, Submission
from models.database import db
from sqlalchemy import func

leaderboard_bp = Blueprint("leaderboard", __name__, url_prefix="/leaderboard")

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

from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Team, User

team_bp = Blueprint("team", __name__, url_prefix="/team")

@team_bp.route("/create", methods=["POST"])
def create_team():
    data = request.json
    team_name = data.get("team_name")
    user_id = data.get("user_id")

    if not team_name or not user_id:
        return jsonify({"error": "Missing fields"}), 400

    if Team.query.filter_by(name=team_name).first():
        return jsonify({"error": "Team name already exists"}), 400

    team = Team(name=team_name, user_id=user_id)
    db.session.add(team)
    db.session.commit()
    return jsonify({"message": "Team created successfully", "team_id": team.id})

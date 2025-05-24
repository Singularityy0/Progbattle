from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Team, User
from sqlalchemy import func

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

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    team = Team(name=team_name, owner_id=user_id)
    team.members.append(user)
    db.session.add(team)
    db.session.commit()
    
    return jsonify({"message": "Team created successfully", "team_id": team.id})

@team_bp.route("/join/<int:team_id>", methods=["POST"])
def join_team(team_id):
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    team = Team.query.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    if len(team.members) >= team.max_size:
        return jsonify({"error": "Team is full"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user in team.members:
        return jsonify({"error": "User already in team"}), 400

    team.members.append(user)
    db.session.commit()
    
    return jsonify({"message": "Successfully joined team"})

@team_bp.route("/leave/<int:team_id>", methods=["POST"])
def leave_team(team_id):
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user ID"}), 400

    team = Team.query.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.id == team.owner_id:
        return jsonify({"error": "Team owner cannot leave the team"}), 400

    if user not in team.members:
        return jsonify({"error": "User not in team"}), 400

    team.members.remove(user)
    db.session.commit()
    
    return jsonify({"message": "Successfully left team"})

@team_bp.route("/list")
def list_teams():
    teams = Team.query.all()
    return jsonify([{
        "id": team.id,
        "name": team.name,
        "members": [{
            "id": member.id,
            "username": member.username
        } for member in team.members],
        "max_size": team.max_size,
        "round": team.round,
        "owner_id": team.owner_id
    } for team in teams])

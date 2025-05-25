from flask import Blueprint, request, jsonify, send_from_directory
import os
import csv
import uuid
import subprocess
from datetime import datetime
from werkzeug.utils import secure_filename
from models.database import db
from models.models import Team, Submission
from sqlalchemy import func

bot_bp = Blueprint("bot", __name__, url_prefix="/bot")

SUBMISSIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "submissions"))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
ENGINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "engine.py"))
BOT1_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bot1.py"))

os.makedirs(SUBMISSIONS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def run_game(bot_file):


    filename = f"{uuid.uuid4()}_{secure_filename(bot_file.filename)}"
    saved_path = os.path.join(SUBMISSIONS_DIR, filename)
    bot_file.save(saved_path)
    game_log = os.path.join(os.path.dirname(ENGINE_PATH), "game_log.csv")
    if os.path.exists(game_log):
        os.remove(game_log)

    result = subprocess.run(
        ["python", ENGINE_PATH, 
         "--p1", saved_path, 
         "--p2", BOT1_PATH],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(ENGINE_PATH)
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("RETURN CODE:", result.returncode)
    if result.returncode != 0:
        raise RuntimeError(f"engine.py failed: {result.stderr}")
    

    game_log = os.path.join(os.path.dirname(ENGINE_PATH), "game_log.csv")
    max_score = {"bot1": 0, "bot2": 0}
    
    with open(game_log, "r") as f:
        reader = csv.reader(f)
        next(reader)  #
        for row in reader:
            score_bot1 = int(row[7])
            score_bot2 = int(row[8])
            if score_bot1 > max_score["bot1"]:
                max_score["bot1"] = score_bot1
            if score_bot2 > max_score["bot2"]:
                max_score["bot2"] = score_bot2
    
    return max_score["bot1"], max_score["bot2"], saved_path

def maybe_qualify_for_round_2():
    completed_teams = (
        db.session.query(func.count(Team.id))
        .filter(Team.round == 1, Team.matches_played >= 10)
        .scalar()
    )
    
    if completed_teams >= 24:
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

        for team_id, _ in top_teams:
            team = Team.query.get(team_id)
            team.is_qualified = True
            team.round = 2

@bot_bp.route("/logs/<path:filename>")
def serve_log(filename):
    try:
        if not os.path.exists(os.path.join(LOG_DIR, filename)):
            return jsonify({"error": "Log file not found"}), 404

        response = send_from_directory(LOG_DIR, filename, as_attachment=True)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Content-Type', 'text/csv')
        return response
    except Exception as e:
        print(f"Error serving log file: {str(e)}")  # Add debugging
        return jsonify({"error": f"Error serving log file: {str(e)}"}), 404

@bot_bp.route("/submit", methods=["POST"])
def submit_bot():
    if "bot_file" not in request.files:
        return jsonify({"error": "No bot file provided"}), 400

    team_id = request.form.get("team_id")
    if not team_id:
        return jsonify({"error": "Team ID required"}), 400

    team = Team.query.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    if team.round == 1 and team.matches_played >= 10:
        return jsonify({"error": "Maximum matches (10) already played for Round 1"}), 400

    bot_file = request.files["bot_file"]
    if bot_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        your_points, system_points, saved_path = run_game(bot_file)

        if your_points > system_points:
            final_score = 5
        elif your_points == system_points:
            final_score = 2
        else:
            final_score = 0


        final_score += your_points // 3
        match_id = str(uuid.uuid4())
        os.makedirs(LOG_DIR, exist_ok=True)
        log_filename = f"match_{match_id}.csv"
        log_path = os.path.join(LOG_DIR, log_filename)
        game_log = os.path.join(os.path.dirname(ENGINE_PATH), "game_log.csv")
        if os.path.exists(game_log):
            os.replace(game_log, log_path)

        submission = Submission(
            team_id=team_id,
            bot_path=saved_path,
            score=round(final_score, 2),
            log_path=log_filename,
            round=team.round
        )
        db.session.add(submission)

        team.matches_played += 1
        

        if team.round == 1 and team.matches_played == 10 and not team.is_qualified:
            maybe_qualify_for_round_2()

        db.session.commit()

        return jsonify({
            "message": "Bot submitted successfully",
            "your_score": your_points,
            "system_score": system_points,
            "final_score": round(final_score, 2),
            "matches_remaining": 10 - team.matches_played if team.round == 1 else None,
            "log_file": log_filename,
            "details": {
                "win_bonus": your_points > system_points,
                "close_match": abs(your_points - system_points) <= 1
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@bot_bp.route("/history/<int:team_id>")
def submission_history(team_id):
    submissions = (
        Submission.query
        .filter_by(team_id=team_id)
        .order_by(Submission.timestamp.desc())
        .all()
    )
    return jsonify([{
        "id": sub.id,
        "score": sub.score,
        "timestamp": sub.timestamp.isoformat(),
        "round": sub.round,
        "logs": sub.log_path.split(",") if sub.log_path else [],
        "bot_path": sub.bot_path
    } for sub in submissions])

import os
import uuid
import subprocess
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, send_from_directory
from models.database import db
from models.models import Submission, Team, User
from werkzeug.utils import secure_filename
from sqlalchemy import func

bot_bp = Blueprint("bot", __name__, url_prefix="/bot")

SUBMISSIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "submissions"))
ENGINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "engine.py"))
BOT1_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bot1.py"))
BOT2_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bot2.py"))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))

MAX_SUBMISSIONS_PER_DAY = 10

def check_submission_limit(team_id):
    today = datetime.utcnow().date()
    submissions_today = (
        Submission.query
        .filter(Submission.team_id == team_id)
        .filter(func.date(Submission.timestamp) == today)
        .count()
    )
    return submissions_today < MAX_SUBMISSIONS_PER_DAY

@bot_bp.route("/logs/<path:filename>")
def serve_log(filename):
    """Serve log files"""
    try:
        response = send_from_directory(LOG_DIR, filename)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        return jsonify({"error": f"Error serving log file: {str(e)}"}), 404

@bot_bp.route("/submit", methods=["POST"])
def submit_bot():
    if "file" not in request.files or "team_id" not in request.form:
        return jsonify({"error": "Missing bot file or team ID"}), 400

    team_id = int(request.form["team_id"])
    team = Team.query.get(team_id)
    if not team:
        return jsonify({"error": "Team not found"}), 404

    if not check_submission_limit(team_id):
        return jsonify({"error": f"Daily submission limit ({MAX_SUBMISSIONS_PER_DAY}) reached"}), 429

    file = request.files["file"]
    filename = secure_filename(file.filename)
    if not filename.endswith('.py'):
        return jsonify({"error": "Only Python files are allowed"}), 400

    # Save uploaded bot with unique ID
    saved_path = os.path.join(SUBMISSIONS_DIR, f"{uuid.uuid4()}_{filename}")
    file.save(saved_path)

    try:
        # Play against system bot (bot1.py)
        match_id = str(uuid.uuid4())
        result = subprocess.run(
            ["python", ENGINE_PATH, "--p1", saved_path, "--p2", BOT1_PATH],
            capture_output=True,
            text=True
        )

        # Get match outcome
        score_line = next((line for line in result.stdout.split('\n') if "Final Score:" in line), None)
        winner_line = next((line for line in result.stdout.split('\n') if "Winner:" in line), None)
        
        if not score_line or not winner_line:
            raise Exception("Could not parse game results")

        # Parse scores and winner
        scores = eval(score_line.split("Score: ")[1])
        winner = winner_line.split("Winner: ")[1].strip()
        your_points = scores['bot1']  # User's bot raw score
        system_points = scores['bot2']  # System bot raw score
        
        # Calculate final score based on win/loss
        # If user wins: (X + Y)/2, if loses: (X - Y)/2
        if winner == 'bot1':  # User won
            final_score = (your_points + system_points) / 2
        else:  # System won
            final_score = (your_points - system_points) / 2
          # Create logs directory if it doesn't exist
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Save game log with unique ID
        log_filename = f"match_{match_id}.csv"
        log_path = os.path.join(LOG_DIR, log_filename)
        if os.path.exists("game_log.csv"):
            os.replace("game_log.csv", log_path)

        # Save submission to database
        submission = Submission(
            team_id=team_id,
            bot_path=saved_path,
            score=round(final_score, 2),  # Save calculated score
            log_path=log_filename,  # Store just the filename
            round=team.round
        )
        db.session.add(submission)
        db.session.commit()

        return jsonify({
            "message": "Match completed",
            "match_result": {
                "your_score": your_points,
                "system_score": system_points,
                "final_score": round(final_score, 2),
                "won": winner == 'bot1',
                "log_file": f"match_{match_id}.csv"
            }
        })

    except Exception as e:
        # Clean up in case of errors
        if os.path.exists(saved_path):
            os.remove(saved_path)
        if os.path.exists("game_log.csv"):
            os.remove("game_log.csv")
        return jsonify({"error": f"Error evaluating bot: {str(e)}"}), 500

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
        "logs": sub.log_path.split(",") if sub.log_path else []
    } for sub in submissions])

import os
import uuid
import subprocess
from flask import Blueprint, request, jsonify
from models.database import db
from models.models import Submission
from werkzeug.utils import secure_filename

bot_bp = Blueprint("bot", __name__, url_prefix="/bot")

SUBMISSIONS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "submissions"))
ENGINE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "engine.py"))
BOT1_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "bot1.py"))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))

@bot_bp.route("/submit", methods=["POST"])
def submit_bot():
    if "file" not in request.files or "team_id" not in request.form:
        return jsonify({"error": "Missing bot file or team ID"}), 400

    file = request.files["file"]
    team_id = request.form["team_id"]
    filename = secure_filename(file.filename)
    saved_path = os.path.join(SUBMISSIONS_DIR, f"{uuid.uuid4()}_{filename}")
    file.save(saved_path)

    # Run the match using subprocess
    result = subprocess.run(
        ["python", ENGINE_PATH, "--p1", saved_path, "--p2", BOT1_PATH],
        capture_output=True,
        text=True
    )

    score = 0
    if "Winner: bot1" in result.stdout:
        score = 1

    match_id = str(uuid.uuid4())
    log_path = os.path.join(LOG_DIR, f"match_{match_id}.csv")
    if os.path.exists("game_log.csv"):
        os.rename("game_log.csv", log_path)

    # Save to database
    submission = Submission(
        team_id=team_id,
        bot_path=saved_path,
        score=score,
        log_path=log_path
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        "message": "Match completed",
        "score": score,
        "log": log_path
    })

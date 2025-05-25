from .database import db
from datetime import datetime


team_members = db.Table(
    "team_members",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("team_id", db.Integer, db.ForeignKey("team.id"))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    teams = db.relationship("Team", secondary=team_members, backref="members")

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    max_size = db.Column(db.Integer, default=4)
    round = db.Column(db.Integer, default=1)  # 1 for system bots, 2 for team vs team
    matches_played = db.Column(db.Integer, default=0)  # Track number of matches played
    is_qualified = db.Column(db.Boolean, default=False)  # Track if qualified for round 2
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submissions = db.relationship("Submission", backref="team", lazy=True)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    bot_path = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    log_path = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    round = db.Column(db.Integer, default=1)
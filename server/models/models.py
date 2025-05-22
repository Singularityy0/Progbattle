from .database import db
from datetime import datetime

# Association table for team members
team_members = db.Table(
    "team_members",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("team_id", db.Integer, db.ForeignKey("team.id"))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    teams = db.relationship("Team", secondary=team_members, backref="members")

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    max_size = db.Column(db.Integer, default=4)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    bot_path = db.Column(db.String(255), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    log_path = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    round = db.Column(db.Integer, default=1)
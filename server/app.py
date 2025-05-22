import os
from flask import Flask
from flask_cors import CORS
from models.database import db

def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, "progbattle_new.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    from routes.auth import auth_bp
    from routes.team import team_bp
    from routes.bot import bot_bp
    from routes.leaderboard import leaderboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(leaderboard_bp)

    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)

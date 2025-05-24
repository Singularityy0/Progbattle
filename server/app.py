from flask import Flask, send_from_directory, send_file
from flask_cors import CORS
from models.database import db
import os


def create_app():
    app = Flask(__name__)

    server_dir = os.path.abspath(os.path.dirname(__file__))
    project_dir = os.path.dirname(server_dir)
    db_path = os.path.join(server_dir, "progbattle_new.db")
    frontend_dir = os.path.join(project_dir, "Frontend")

    print("Debugging paths:")
    print(f"Server directory: {server_dir}")
    print(f"Project directory: {project_dir}")
    print(f"Frontend directory: {frontend_dir}")
    print(f"Frontend exists: {os.path.exists(frontend_dir)}")
    if os.path.exists(frontend_dir):
        print(f"Frontend contents: {os.listdir(frontend_dir)}")

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    # Blueprints
    from routes.auth import auth_bp
    from routes.team import team_bp
    from routes.bot import bot_bp
    from routes.leaderboard import leaderboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(leaderboard_bp)

    # Serve frontend
    @app.route('/')
    def serve_index():
        try:
            index_path = os.path.join(frontend_dir, 'index.html')
            print(f"Attempting to serve index from: {index_path}")
            if not os.path.exists(index_path):
                print(f"Index file not found at: {index_path}")
                return "Index file not found", 404
            return send_file(index_path)
        except Exception as e:
            print(f"Error serving index: {str(e)}")
            return str(e), 500

    @app.route('/<path:filename>')
    def serve_static(filename):
        try:
            file_path = os.path.join(frontend_dir, filename)
            print(f"Attempting to serve: {file_path}")
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                # For SPA, return index.html for non-asset paths
                if not filename.endswith(('.js', '.css', '.ico', '.png', '.jpg', '.jpeg', '.gif')):
                    return send_file(os.path.join(frontend_dir, 'index.html'))
                return f"File not found: {filename}", 404
            return send_file(file_path)
        except Exception as e:
            print(f"Error serving {filename}: {str(e)}")
            return str(e), 500

    return app


app = create_app()

with app.app_context():
    db.create_all()

@app.route('/static/<path:filename>')
def static_logs(filename):
    logs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs'))
    return send_from_directory(logs_path, filename)


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    from app.routes import main, projects, automation, voice
    app.register_blueprint(main.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(automation.bp)
    app.register_blueprint(voice.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app 
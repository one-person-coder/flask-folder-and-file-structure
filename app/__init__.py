from flask import Flask
from app.config import Config
from app.extensions import db, migrate, cors
from app.routes.auth import login, auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app

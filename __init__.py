import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .extensions import db
from .models import User, Project, Site, Metric
from .routes import api

def create_app(test_config=None):
    app=Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL","sqlite:///darukaa_dev.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY","dev-only-change-me"),
    )
    if test_config: app.config.update(test_config)
    db.init_app(app); JWTManager(app)
    CORS(app, origins=os.getenv("CORS_ORIGINS","http://localhost:5173").split(","))
    app.register_blueprint(api, url_prefix="/api")
    with app.app_context():
        db.create_all()
    return app

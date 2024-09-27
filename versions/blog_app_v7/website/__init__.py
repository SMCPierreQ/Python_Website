import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    # Create flask application and define static folder for app
    app = Flask(__name__, static_folder='static')
    # Secret key for app configuration
    app.config['SECRET_KEY'] = "lNJrn@]@neV]O.h"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Post, Comment

    # Create database if it doesn't exist
    with app.app_context():
        db.create_all()

    # Initialize LoginManager for user session
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Loads user using login manager from the database using their ID
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

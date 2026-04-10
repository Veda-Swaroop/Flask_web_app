from flask import Flask, flash, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_migrate import Migrate
from app.extensions import db
from app.models import User
from dotenv import load_dotenv
import os

load_dotenv()

csrf = CSRFProtect()
login_manager = LoginManager()



def create_app():
    app = Flask(__name__)
   
    # Config
    database_url = os.environ.get("DATABASE_URL", "")
    database_url = database_url.replace("postgres://", "postgresql+psycopg2://").replace("postgresql://", "postgresql+psycopg2://")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    # app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE")
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    # app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY")


    # init extensions
    csrf.init_app(app)
    db.init_app(app)

    # Flask Migrate
    migrate = Migrate(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login" #type:ignore
    login_manager.login_message = "Please login first!"
    login_manager.login_message_category = "warning"



    # register blueprints
    from app.main import main
    from app.auth import auth
    from app.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    

    # load user for flask-login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    return app


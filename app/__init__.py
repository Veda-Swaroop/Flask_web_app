from flask import Flask, flash, redirect, url_for
from flask_login import LoginManager
from app.extensions import db
from app.models import Users




def create_app():
    app = Flask(__name__)

    # Config
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    # app.config["SQLALCHEMY_BINDS"] = {'books_db': f"sqlite:///books.db"}
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "some_random_secret"


    # init extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login" #type:ignore
    db.init_app(app)


    # register routes
    from app.main import main
    from app.auth import auth
    from app.admin import admin

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    

    # Create Tables
    with app.app_context():
        db.create_all()

    # load user for flask-login
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    
    # handle unauthorized login
    @login_manager.unauthorized_handler
    def unauthorized():
        flash("Please login first!", "warning")
        return redirect(url_for("auth.login"))



    return app


from flask import Blueprint, render_template, session, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models import Users
from app.forms import LoginForm, RegisterForm, ResetForm, VerifyForm

auth = Blueprint("auth", __name__)


@auth.route("/")
def index():
    form = LoginForm()
    return render_template("index.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():

        usr_name = form.username.data
        pwd = form.password.data

        if not usr_name or not pwd:
            flash("Enter username and password", "danger")
            return redirect(url_for("auth.login"))
        
        user = Users.query.filter_by(username=usr_name).first()

        if user and check_password_hash(user.password, pwd):
            login_user(user)

            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            
            return redirect(url_for("main.home"))
            
        flash("Invalid Username or Password!", "danger")
           
    return render_template("index.html", form=form)



# Logout Route
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out!", "success")
    return render_template("logout.html")




# Register Route
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():

        usr_name = form.username.data
        pwd = form.password.data
 
        user = Users(
            username = usr_name,                     #type:ignore
            password = generate_password_hash(pwd)   #type:ignore
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)



# Verify Route
@auth.route("/verify", methods=["GET", "POST"])
def verify():
    form = VerifyForm()

    if form.validate_on_submit():

        usr_name = form.username.data

        user = Users.query.filter_by(username=usr_name).first()
    
        if user and usr_name != "admin":
            session["reset_user_id"] = user.id
            return redirect(url_for("auth.reset"))
        
        else:
            flash("Invalid Username", "danger")
            
            
    return render_template("verify.html", form=form)



# Reset Route
@auth.route("/reset", methods=["GET", "POST"])
def reset():
        
    if "reset_user_id" not in session:
        flash("Please verify your account!", "danger")
        return redirect(url_for("auth.verify"))
    
    
    form = ResetForm()

    if form.validate_on_submit():

        new_pwd = form.new_password.data or ""
        user_id = session.get("reset_user_id")

        if user_id is None:
            flash("Session expired. Please verify again.", "danger")
            return redirect(url_for("auth.verify"))

        user = Users.query.get(int(user_id))

        if user:
            user.password = generate_password_hash(new_pwd)
            db.session.commit()

            session.pop("reset_user_id", None)

            flash("Password reset successful!", "success")
            return redirect(url_for("auth.login"))
        
        else:
            flash("Invalid user. Please verify again.", "danger")
            return redirect(url_for("auth.verify"))

    return render_template("reset.html", form=form)
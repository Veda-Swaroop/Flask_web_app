from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import Users

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        usr_name = request.form.get("username")
        pwd = request.form.get("password")

        if not usr_name or not pwd:
            flash("Enter username and password", "danger")
            return redirect(url_for("auth.login"))
        
        if len(usr_name) < 3:
            flash("username must be atleast 3 characters", "warning")
        
        if len(pwd) < 4:
            flash("password must be atleast 4 characters", "warning")
        
        user = Users.query.filter_by(username=usr_name).first()

        if user and check_password_hash(user.password, pwd):
            login_user(user)

            if user.is_admin:
                return redirect(url_for("admin.dashboard"))
            
            return redirect(url_for("main.home"))
            
        flash("Invalid Username or Password!", "danger")
        return redirect(url_for("auth.login"))    
        
    return render_template("index.html")

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
    if request.method == "POST":

        usr_name = request.form.get("username")
        pwd = request.form.get("password")

        if not usr_name or len(usr_name) < 3:
            flash("username must be atleast 3 characters", "warning")
            return redirect(url_for("auth.register"))

        if not pwd or len(pwd) < 4:
            flash("password must be atleast 4 characters", "warning")
            return redirect(url_for("auth.register"))
            

        existing = Users.query.filter_by(username=usr_name).first()
        if existing:
            flash("Username already exists!", "danger")
            return redirect(url_for("auth.register"))
        
        
        user = Users(
            username = usr_name,                     #type:ignore
            password = generate_password_hash(pwd)   #type:ignore
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

# Verify Route
@auth.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        usr_name = request.form.get("username")

        if not usr_name:
            flash("Enter Username!", "warning")
            return redirect(url_for("auth.verify"))

        user = Users.query.filter_by(username=usr_name).first()
    
        if user and usr_name != "admin":
            return render_template("reset.html", user_id=user.id)
        else:
            flash("Invalid Username", "danger")
            return redirect(url_for("auth.verify"))
            
    return render_template("verify.html")

# Reset Route
@auth.route("/reset", methods=["GET", "POST"])
def reset():

    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_pwd = request.form.get("new_password")
        confirm_pwd = request.form.get("confirm_password")

        if not user_id:
            flash("Verify your account!", "danger")
            return redirect(url_for("auth.verify"))

        if not new_pwd or not confirm_pwd:
            flash("Enter new password and confirm password", "warning")
            return redirect(url_for("auth.reset"))

        if new_pwd != confirm_pwd:
            flash("Passwords do not match!", "danger")
            return render_template("reset.html", user_id=user_id)
       
        user = Users.query.get(int(user_id))
        
        if not user:
            flash("Invalid user, Please verify!", "danger")
            return redirect(url_for("auth.verify"))
        
        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        flash("Password reset successful!", "success")
        return redirect(url_for("auth.login"))
    
    return render_template("reset.html")
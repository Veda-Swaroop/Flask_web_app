# app/routes.py
from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
from .models import Users

main = Blueprint("main", __name__)




@main.route("/")
def index():
    return render_template("index.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        usr_name = request.form.get("username")
        pwd = request.form.get("password")

        if not usr_name or not pwd:
            flash("Enter username and password", "danger")
            return redirect(url_for("main.login"))
        
        if len(usr_name) < 3:
            flash("username must be atleast 3 characters", "warning")
        
        if len(pwd) < 4:
            flash("password must be atleast 4 characters", "warning")
        
        user = Users.query.filter_by(username=usr_name).first()

        if user and check_password_hash(user.password, pwd):
            session["user_id"] = user.id
            session["username"] = user.username

            if user.is_admin:
                return redirect(url_for("main.admin"))
            
            return redirect(url_for("main.home"))
            
        flash("Invalid Username or Password!", "danger")
        return redirect(url_for("main.login"))    
        
    return render_template("index.html")

@main.route("/logout")
def logout():
    session.clear()
    flash("You have successfully logged out!", "success")
    return render_template("logout.html")

@main.route("/home")
def home():
    if "username" not in session:
        flash("Please login first!", "warning") 
        return redirect(url_for("main.login"))
    return render_template("home.html", name=session["username"])


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        usr_name = request.form.get("username")
        pwd = request.form.get("password")

        if not usr_name or len(usr_name) < 3:
            flash("username must be atleast 3 characters", "warning")
            return redirect(url_for("main.register"))

        if not pwd or len(pwd) < 4:
            flash("password must be atleast 4 characters", "warning")
            return redirect(url_for("main.register"))
            

        existing = Users.query.filter_by(username=usr_name).first()
        if existing:
            flash("Username already exists!", "danger")
            return redirect(url_for("main.register"))
        
        
        user = Users(
            username = usr_name,
            password = generate_password_hash(pwd)
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/admin", methods = ["GET", "POST"])
def admin():
    if "user_id" not in session or session["username"] != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("main.login"))
    
    if request.method == "POST":
        account_id = request.form.get("id")
        
        if account_id:
            user = Users.query.get(int(account_id))
            if user:
                db.session.delete(user)
                db.session.commit()

    accounts = Users.query.all()
    return render_template("admin.html", accounts=accounts)


@main.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        usr_name = request.form.get("username")

        if not usr_name:
            flash("Enter Username!", "warning")
            return redirect(url_for("main.verify"))

        user = Users.query.filter_by(username=usr_name).first()
    
        if user and usr_name != "admin":
            return render_template("reset.html", user_id=user.id)
        else:
            flash("Invalid Username", "danger")
            return redirect(url_for("main.verify"))
            
    return render_template("verify.html")



@main.route("/reset", methods=["GET", "POST"])
def reset():

    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_pwd = request.form.get("new_password")
        confirm_pwd = request.form.get("confirm_password")

        if not user_id:
            flash("Verify your account!", "danger")
            return redirect(url_for("verify"))

        if not new_pwd or not confirm_pwd:
            flash("Enter new password and confirm password", "warning")
            return redirect(url_for("reset"))

        if new_pwd != confirm_pwd:
            flash("Passwords do not match!", "danger")
            return render_template("reset.html", user_id=user_id)
       
        user = Users.query.get(int(user_id))
        
        if not user:
            flash("Invalid user!", "danger")
            return redirect(url_for("verify"))
        
        user.password = generate_password_hash(new_pwd)
        db.session.commit()

        flash("Password reset successful!", "success")
        return redirect(url_for("main.login"))
    
    return render_template("reset.html")



@main.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if q:
        results = db.session.query(Book).filter(Book.title.ilike(f"%{q}%")).limit(50).all() 
        titles = [{"title":book.title} for book in results] 
    
    else:
        titles = []
    return jsonify(titles)
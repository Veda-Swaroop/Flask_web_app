from flask import Flask, render_template, request, session, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from extensions import db


app = Flask(__name__)

app.config["SESSION_PERMANENT"] =  False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "some_random_secret"
Session(app)

db.init_app(app)


from models import User


with app.app_context():
    db.create_all()



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        usr_name = request.form.get("username")
        pwd = request.form.get("password")

        if not usr_name or not pwd:
            flash("Enter username and password", "danger")
            return redirect(url_for("login"))
        
        if len(usr_name) < 3:
            flash("username must be atleast 3 characters", "warning")
        
        if len(pwd) < 4:
            flash("password must be atleast 4 characters", "warning")
        
        user = User.query.filter_by(username=usr_name).first()

        if user and check_password_hash(user.password, pwd):
            session["user_id"] = user.id
            session["username"] = user.username

            if user.is_admin:
                return redirect(url_for("admin"))
            
            return redirect(url_for("home"))
            
        flash("Invalid Username or Password!", "danger")
        return redirect(url_for("login"))    
        
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have successfully logged out!", "success")
    return render_template("logout.html")

@app.route("/home")
def home():
    if "username" not in session:
        flash("Please login first!", "warning") 
        return redirect(url_for("login"))
    return render_template("home.html", name=session["username"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        usr_name = request.form.get("username")
        pwd = request.form.get("password")

        if not usr_name or len(usr_name) < 3:
            flash("username must be atleast 3 characters", "warning")
            return redirect(url_for("register"))

        if not pwd or len(pwd) < 4:
            flash("password must be atleast 4 characters", "warning")
            return redirect(url_for("register"))
            

        existing = User.query.filter_by(username=usr_name).first()
        if existing:
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        
        
        user = User(
            username = usr_name,
            password = generate_password_hash(pwd)
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/admin", methods = ["GET", "POST"])
def admin():
    if "user_id" not in session or session["username"] != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        account_id = request.form.get("id")
        
        if account_id:
            user = User.query.get(int(account_id))
            if user:
                db.session.delete(user)
                db.session.commit()

    accounts = User.query.all()
    return render_template("admin.html", accounts=accounts)


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        usr_name = request.form.get("username")

        if not usr_name:
            flash("Enter Username!", "warning")
            return redirect(url_for("verify"))

        user = User.query.filter_by(username=usr_name).first()
    
        if user and usr_name != "admin":
            return render_template("reset.html", user_id=user.id)
        else:
            flash("Invalid Username", "danger")
            return redirect(url_for("verify"))
            
    return render_template("verify.html")



@app.route("/reset", methods=["GET", "POST"])
def reset():

    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_pwd = request.form.get("new_password")
        confirm_pwd = request.form.get("confirm_password")
        

        if not user_id:
            flash("User ID missing", "danger")
            return redirect(url_for("verify"))

        if not new_pwd or not confirm_pwd:
            flash("Enter new password and confirm password", "warning")
            return redirect(url_for("reset"))


        if new_pwd != confirm_pwd:
            flash("Passwords do not match!", "danger")
            return render_template("reset.html", user_id=user_id)
       
        user = User.query.get(int(user_id))
       
        if not user:
            flash("Invalid user!", "danger")
            return redirect(url_for("verify"))
        
        user.pwd = generate_password_hash(new_pwd)
        db.session.commit()

        flash("Password reset successful!", "success")
        return redirect(url_for("login"))
    
    return render_template("reset.html")


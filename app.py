from flask import Flask, render_template, request, session, redirect, flash, url_for, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import sqlite3

app = Flask(__name__)

app.config["SESSION_PERMANENT"] =  False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "some_random_secret"
Session(app)

#db = SQL("sqlite:///data.db")
DATABASE = "data.db"


def get_db() -> sqlite3.Connection:
    db = getattr(g, "db", None)

    if db is None:
        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        g.db = db

    return db
    

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)

    if db is not None:
        db.close()



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usr_name = request.form.get("username")
        pwd = request.form.get("password")

        if usr_name and pwd:
            db = get_db()
            row = db.execute("SELECT * FROM accounts WHERE username = ?", (usr_name,)).fetchone()

            if row and check_password_hash(row["password"], pwd):
                session["user_id"] = row["id"]
                session["username"] = row["username"]

                if usr_name == "admin":
                    return redirect (url_for("admin"))

                return redirect(url_for("home"))
            
            else:
                flash("Invalid Username or Password!", "danger")
                return redirect(url_for("login"))
        # else:
        #     flash("Enter username and password", "danger")
        
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
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
        db = get_db()
        existing = db.execute("SELECT id FROM accounts WHERE username = ?", (usr_name,)).fetchone()
        if existing:
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))
        
        pwd = request.form.get("password")
        if pwd:
            hashed_pwd = generate_password_hash(pwd)
            db = get_db()
            db.execute("INSERT INTO accounts (username, password) VALUES (?, ?)", (usr_name, hashed_pwd))
            db.commit()
            flash("Account created successfully!", "success")
            return redirect(url_for("login"))
        else:
            flash("Enter Password!", "warning")


    return render_template("register.html")


@app.route("/admin", methods = ["GET", "POST"])
def admin():
    if "user_id" not in session or session["username"] != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        account_id = request.form.get("id")
        
        if account_id:
            db = get_db()
            db.execute("DELETE FROM accounts WHERE id = ?", (int(account_id),))
            db.commit()

    db = get_db()
    accounts = db.execute("SELECT * FROM accounts").fetchall()
    return render_template("admin.html", accounts=accounts)


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        usr_name = request.form.get("username")

        if not usr_name:
            flash("Enter Username!", "warning")
            return render_template("verify.html")

        db = get_db()
        row = db.execute("SELECT id FROM accounts WHERE username = ?", (usr_name,)).fetchone()
    
        if row:
            return render_template("reset.html", user_id=row["id"])
        else:
            flash("Invalid Username", "danger")
            
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


        db = get_db()

       
        user = db.execute("SELECT id FROM accounts WHERE id = ?", (int(user_id),)).fetchone()
       
        if not user:
            flash("Invalid user!", "danger")
            return redirect(url_for("verify"))
        
        hashed_pwd = generate_password_hash(new_pwd)
        db.execute("UPDATE accounts SET password = ? WHERE id = ?", (hashed_pwd, int(user_id)))
        db.commit()
        flash("Password reset successful!", "success")
        return redirect(url_for("login"))
    


    return render_template("reset.html")


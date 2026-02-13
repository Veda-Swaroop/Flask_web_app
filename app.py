from flask import Flask, render_template, request, session, redirect, flash
from flask_session import Session
from cs50 import SQL

app = Flask(__name__)

app.config["SESSION_PERMANENT"] =  False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = "some_random_secret"
Session(app)

db = SQL("sqlite:///data.db")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usr_name = request.form.get("username")
        pwd = request.form.get("password")
        if usr_name and pwd:
            rows = db.execute("SELECT * FROM accounts WHERE username = ? AND password = ?", usr_name, pwd)
            if len(rows) == 1:
                if usr_name == "admin":
                    return redirect ("/admin")
                
                session["username"] = usr_name
                session["password"] = pwd
                return redirect("/home")
            
            else:
                flash("Invalid Username or Password!", "danger")
                return redirect("/login")
        # else:
        #     flash("Enter username and password", "danger")
        
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

@app.route("/home")
def home():
    return render_template("home.html", name=session["username"])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        usr_name = request.form.get("username")
        pwd = request.form.get("password")
        db.execute("INSERT INTO accounts (username, password) VALUES (?, ?)", usr_name, pwd)
        flash("Account created successfully!", "success")
        return render_template("register.html", message="success")

    return render_template("register.html")


@app.route("/admin", methods = ["GET", "POST"])
def admin():
    if request.method == "POST":
        account_id = request.form.get("id")
        if account_id:
            db.execute("DELETE FROM accounts WHERE id = ?", int(account_id))

    accounts = db.execute("SELECT * FROM accounts")
    return render_template("admin.html", accounts=accounts)


@app.route("/verify", methods=["GET", "POST"])
def verify():
    usr_name = request.form.get("username")
    if usr_name:
        row = db.execute("SELECT id FROM accounts WHERE username = ?", usr_name)
        #print(row[0]["id"])
        if len(row) == 1:
            return render_template("reset.html", row=row[0]["id"])
        else:
            flash("Invalid Username", "danger")


    return render_template("reset.html")



@app.route("/reset", methods=["GET", "POST"])
def reset():
    new_pwd = request.form.get("new_password")
    confirm_pwd = request.form.get("confirm_password")
    row = request.form.get("user_id")

    if row:
        # print("Row is:", int(row))
        # print("Hello")

        if new_pwd and confirm_pwd:
            if new_pwd != confirm_pwd:
                flash("Passwords do not match!", "danger")
        
            else:
                db.execute("UPDATE accounts SET password = ? WHERE id = ?", new_pwd, int(row))
                flash("Password reset successful", "success")
                return render_template("reset.html", message="success")
            
        else:
            flash("Enter new password and confirm password", "warning")
        
        
    else:
        flash("Username is missing!", "danger")
        return redirect("/")


    return render_template("reset.html")


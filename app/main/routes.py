from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Book

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/home")
@login_required
def home():
    return render_template("home.html", name=current_user.username)


@main.route("/search")
def search():
    q = request.args.get("q", "").strip()
    if q:
        results = db.session.query(Book).filter(Book.title.ilike(f"%{q}%")).limit(50).all() 
        titles = [{"title":book.title} for book in results] 
    
    else:
        titles = []
    return jsonify(titles)
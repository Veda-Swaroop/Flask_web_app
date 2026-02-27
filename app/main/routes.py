from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import current_user, login_required

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
@login_required
def search():
    q = request.args.get("q", "").strip()
    if q:
        results = Book.query.filter(Book.title.ilike(f"%{q}%")).limit(10).all()
        titles = [{"id":book.bookID, "title":book.title} for book in results] 
    
    else:
        titles = []
    return jsonify(titles)


@main.route("/book_details/<int:id>")
@login_required
def book_details(id):
    book = Book.query.get_or_404(id)
    return render_template("book_detail.html", book=book)




@main.route("/add_to_cart/<int:book_id>", methods=["POST"])
@login_required
def add_to_cart(book_id):
    if "cart" not in session:
        session["cart"] = []

    if book_id not in session["cart"]:
        session["cart"].append(book_id)
        session.modified = True
        flash("Book added to cart successfully", "success")
    else:
        flash("This book is already in your cart", "info")

    return redirect(url_for("main.book_details", id=book_id))
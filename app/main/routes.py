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
    page = request.args.get("page", 1, type=int)
    books = Book.query.paginate(page=page, per_page=10)

    window_size = 10

    if page <= (books.pages - window_size):

        min = 0 + page
        max = window_size + page

    else:

        min = books.pages - window_size
        max = books.pages + 1

    sliding_window = range(min, max)

    return render_template("home.html", name=current_user.username, books=books, w_range=sliding_window)


@main.route("/search")
@login_required
def search():
    q = request.args.get("q", "").strip()
    if q:
        results = Book.query.filter(Book.title.ilike(f"{q}%")).limit(10).all()
        titles = [{"id":book.bookID, "title":book.title} for book in results] 
    
    else:
        titles = []
    return jsonify(titles)


@main.route("/book_details/<int:book_id>", methods=["GET", "POST"])
@login_required
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template("book_detail.html", book=book)




@main.route("/add_to_cart/<int:book_id>", methods=["GET","POST"])
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

    return redirect(request.referrer)


@main.route("/check_cart", methods=["GET", "POST"])
@login_required
def check_cart():
    if "cart" not in session or session["cart"] == []:
        flash("No books in cart", "warning")
        return render_template("cart.html")

    books = Book.query.filter(Book.bookID.in_(session["cart"]))
    return render_template("cart.html", books=books)


@main.route("/delete_from_cart/<int:book_id>", methods=["POST"])
@login_required
def delete_from_cart(book_id):
    if "cart" not in session or session["cart"] == []:
        flash("No books in cart!", "warning")
    else:
        cart = session.get("cart", [])
        cart.remove(book_id)
        session["cart"] = cart
        flash("Book deleted!", "success")
    return redirect("/check_cart")
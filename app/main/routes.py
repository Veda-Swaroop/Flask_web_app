from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, send_from_directory
from flask_login import current_user, login_required
from app.extensions import db
import os, textwrap

from app.models import Book, Cart

main = Blueprint("main", __name__)


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




@main.route("/add_to_cart/<int:book_id>", methods=["POST"])
@login_required
def add_to_cart(book_id):
    
    book = Book.query.get(book_id)

    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404
    
    cart_item = Cart.query.filter_by(user_id = current_user.id, book_id=book_id).first()
    
    title = book.title
    short_title = textwrap.shorten(title,width=30, placeholder="...." )
    
    if cart_item:
        cart_item.quantity += 1
        message = f"Updated quantity for Book: '{short_title}'"
        category = "info"
    else:
        new_item = Cart(user_id=current_user.id, book_id=book_id) #type: ignore
        db.session.add(new_item)
        message = f" Book: '{short_title}' Added to cart"
        category = "success"
    
    db.session.commit()
    # return redirect(request.referrer or url_for("main.home"))
    return jsonify({
        "status": "success",
        "message": message,
        "category": category,
    }), 200


@main.route("/check_cart", methods=["GET", "POST"])
@login_required
def check_cart():
    user_cart = current_user.cart_items

    if not user_cart:
        flash("No books in cart", "warning")
        return render_template("cart.html")

    return render_template("cart.html", cart=user_cart)


@main.route("/delete_from_cart/<int:book_id>", methods=["POST"])
@login_required
def delete_from_cart(book_id):

    cart_item = Cart.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        
    if not cart_item:
        return jsonify({"status": "error", "message": "Item not found in cart"}), 404
    
    book = Book.query.get(book_id)
    title = book.title #type:ignore
    short_title = textwrap.shorten(title,width=30, placeholder="...." )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.session.commit()
        return jsonify({
            "status": "success",
            "action": "decremented",
            "new_quantity": cart_item.quantity,
            "message": f"Decreased quanity for '{short_title}'",
            "category": "info",
        }), 200


    else:
        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({
            "status": "success",
            "action": "removed",
            "message": f"Removed '{short_title}' from cart",
            "category": "success",
        }), 200



@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
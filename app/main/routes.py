from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, send_from_directory
from flask_login import current_user, login_required
from app.extensions import db
import os, textwrap

from app.models import Book, Cart, CartItem, Order, OrderItem

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
    
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404
    
    cart = Cart.query.filter_by(user_id = current_user.id).first()

    if not cart:
        cart = Cart(user_id = current_user.id) #type:ignore
        db.session.add(cart)
        db.session.commit()
         

    cart_item = CartItem.query.filter_by(cart_id = cart.id, book_id=book_id).first()
    
    title = book.title
    short_title = textwrap.shorten(title,width=30, placeholder="...." )
    
    if cart_item:
        cart_item.quantity += 1
        db.session.commit()
        return jsonify(
            {
                "status": "success",
                "action": "incremented",
                "new_quantity": cart_item.quantity,
                "message": f"Increased quantity for book: '{short_title}'",
                "category": "info",
            }
        ), 200

    else:
        new_item = CartItem(cart_id = cart.id, book_id=book_id, quantity = 1) #type:ignore
        db.session.add(new_item)
        db.session.commit()

        return jsonify({
            "status": "success",
            "action": "added",
            "message": f" Added '{short_title}' to cart",
            "category": "success",
        }), 200


@main.route("/delete_from_cart/<int:book_id>", methods=["POST"])
@login_required
def delete_from_cart(book_id):

    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({"status": "error", "message": "Book not found"}), 404

    cart = Cart.query.filter_by(user_id=current_user.id).first()

    if not cart:
        return jsonify({"status": "error", "message": "Cart not found"}), 404

        
    cart_item = CartItem.query.filter_by(cart_id = cart.id, book_id=book_id).first()

    if not cart_item:
        return jsonify({"status": "error", "message": "Item not found in cart"}), 404
    

    
    title = book.title #type:ignore
    short_title = textwrap.shorten(title,width=30, placeholder="...." )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.session.commit()
        return jsonify({
            "status": "success",
            "action": "decremented",
            "new_quantity": cart_item.quantity,
            "message": f"Decreased quantity for book: '{short_title}'",
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



@main.route("/check_cart", methods=["GET", "POST"])
@login_required
def check_cart():
    cart = current_user.cart

    cart_items = cart.items if cart else []

    if not cart_items:
        flash("No books in cart", "warning")
        return render_template("cart.html")

    return render_template("cart.html", cart=cart_items)


@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')




@main.route("/buy", methods=["GET", "POST"])
@login_required
def buy_items():

    cart_items = current_user.cart.items

    if not cart_items:
        flash("Cart is empty!", "warning")
        return redirect(url_for("main.check_cart"))

    return render_template("order.html", items=cart_items)

@main.route("/order", methods=["POST"])
@login_required
def orders():

    cart = current_user.cart
    if not cart or not cart.items:
        flash("Cart is Empty!", "warning")
        return redirect(url_for("main.check_cart"))
    order = Order(user_id=current_user.id, status="completed") #type:ignore
    db.session.add(order)
    db.session.flush()

    cart_items = cart.items
    order_items = []
    for item in cart_items:
        order_items.append(OrderItem(book_id=item.book.bookID, quantity=item.quantity, order_id=order.id)) #type:ignore

    db.session.add_all(order_items)
    db.session.flush()
   

    for item in cart_items:
        db.session.delete(item)
        
    db.session.commit()

    return redirect(url_for("main.order_confirmation", order_id=order.id))


@main.route("/order_confirmation/<int:order_id>", methods=["GET"])
@login_required
def order_confirmation(order_id):
    
    order = Order.query.get_or_404(order_id)
    return render_template("order_confirmation.html", items=order.order_items)


@main.route("/my_orders", methods=["GET"])
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    if not orders:
        flash("You have no past orders.", "info")
        return render_template("my_orders.html", orders=[])
    
    return render_template("my_orders.html", orders=orders)
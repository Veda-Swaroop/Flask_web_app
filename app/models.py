from app.extensions import db
from flask_login import UserMixin


class Users(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    cart_items = db.relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Users(id = {self.id}, username = {self.username}, password = {self.password}, is_admin = {self.is_admin})>"


class Book(db.Model):
    __tablename__ = 'books'

    # __bind_key__ = 'books_db'

    bookID = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    authors = db.Column(db.Text)
    average_rating = db.Column(db.Float)
    isbn = db.Column(db.Text)
    isbn13 = db.Column(db.Integer)
    language_code = db.Column(db.Text)
    num_pages = db.Column(db.Integer)
    ratings_count = db.Column(db.Integer)
    text_reviews_count = db.Column(db.Integer)
    publication_date = db.Column(db.Text)
    publisher = db.Column(db.Text)

    cart_items = db.relationship("Cart", back_populates="book")

    def __repr__(self) -> str:
        return f"<Book(id={self.bookID}, title={self.title}, author={self.authors}, rating={self.average_rating})>"


class Cart(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.bookID'), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    user = db.relationship("Users", back_populates="cart_items")
    book = db.relationship("Book", back_populates="cart_items")

    __table__args__ = (db.UniqueConstraint('user_id', 'book_id', name='_user_book_uc'),)
    



from app.extensions import db
from flask_login import UserMixin


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)


    def __init__(self, username, password, is_admin=False):
        self.username=username
        self.password=password
        self.is_admin=is_admin


class Book(db.Model):
    __tablename__ = 'books'

    __bind_key__ = 'books_db'

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

    def __repr__(self) -> str:
        return f"<Book {self.bookID}: {self.title} by {self.authors}>"


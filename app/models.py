from app.extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, Numeric, Integer, ForeignKey, DateTime, func
from decimal import Decimal
from datetime import date, datetime
from typing import List, Optional


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    cart: Mapped[Optional["Cart"]] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    
    def __repr__(self) -> str:
        return f"<Users(id = {self.id}, username = {self.username})>"


class Book(db.Model):
    __tablename__ = 'books'

    bookID: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    authors: Mapped[str] = mapped_column(Text)
    average_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    isbn: Mapped[str] = mapped_column(String(20))
    isbn13: Mapped[str] = mapped_column(String(13))
    language_code: Mapped[str] = mapped_column(String(10))
    num_pages: Mapped[int] = mapped_column(Integer)
    ratings_count: Mapped[int] = mapped_column(Integer)
    text_reviews_count: Mapped[int] = mapped_column(Integer)
    publication_date: Mapped[date] = mapped_column()
    publisher: Mapped[str] = mapped_column(Text)


    def __repr__(self) -> str:
        return f"<Book(id={self.bookID}, title={self.title}, author={self.authors}, rating={self.average_rating})>"


class Cart(db.Model):
    __tablename__ = 'carts'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)

    user: Mapped["User"] = relationship(back_populates="cart")
    items: Mapped[List["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")


    

class CartItem(db.Model):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.bookID"))
    quantity: Mapped[int] = mapped_column(server_default="1")

    cart: Mapped["Cart"] = relationship(back_populates="items")
    book: Mapped["Book"] = relationship("Book")


class Order(db.Model):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(20), server_default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


    user: Mapped["User"] = relationship("User", back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.bookID"))
    quantity: Mapped[int] = mapped_column(server_default="1")
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))

    order: Mapped["Order"] = relationship("Order", back_populates="order_items")
    book: Mapped["Book"] = relationship("Book")
    


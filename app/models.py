from flask_login import UserMixin

from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from datetime import datetime

Base =  declarative_base()

class User(Base, UserMixin):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    email = Column(String(120), unique=True)
    phone = Column(String(80), unique=True)
    password_hash = Column(String(256))

book_genre = Table(
    'book_genre',
    Base.metadata,
    Column('book_id', ForeignKey('books.id'), primary_key=True),
    Column('genre_id', ForeignKey('genres.id'), primary_key=True),
    )

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    author = Column(String(300), nullable=False)
    year = Column(Integer)
    price = Column(Float, nullable=False)
    rating = Column(Float)

    cover = Column(String(500))
    description = Column(Text)

    genres = relationship('Genre', secondary=book_genre, backref='books')
    stock = relationship('Stock', uselist=False,
                         back_populates='book', cascade='all, delete-orphan')
    reviews = relationship('Review', back_populates='book')

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True)
    book_id = Column(ForeignKey('books.id'), unique=True)
    quantity = Column(Integer, nullable=False, default=0)

    book = relationship('Book', back_populates='stock')

class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    book_id = Column(ForeignKey('books.id'))
    quantity = Column(Integer, nullable=False)

    user = relationship('User')
    book = relationship('Book')

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    date = Column(DateTime, default=datetime.utcnow())
    status = Column(String(50), default='new')
    address = Column(String)

    items = relationship('OrderItem',
                         back_populates='order', cascade='all, delete-orphan')

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('orders.id'))
    book_id = Column(ForeignKey('books.id'))

    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    order = relationship('Order', back_populates='items')
    book = relationship('Book')

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    book_id = Column(ForeignKey('books.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    score = Column(Float)
    review = Column(Text)

    user = relationship('User')
    book = relationship('Book', back_populates='reviews')


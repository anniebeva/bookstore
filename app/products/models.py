from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship

from app.database import Base

from datetime import datetime


book_genre = Table(
    'book_genre',
    Base.metadata,
    Column('book_id', ForeignKey('products.id'), primary_key=True),
    Column('genre_id', ForeignKey('genres.id'), primary_key=True),
    )

class Book(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    author = Column(String(300), nullable=False)
    year = Column(Integer)
    price = Column(Float, nullable=False)
    rating = Column(Float)

    cover = Column(String(500))
    description = Column(Text)

    genres = relationship('Genre', secondary=book_genre, backref='products')
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
    book_id = Column(ForeignKey('products.id'), unique=True)
    quantity = Column(Integer, nullable=False, default=0)

    book = relationship('Book', back_populates='stock')


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    book_id = Column(ForeignKey('products.id'))
    created_at = Column(DateTime, default=datetime.utcnow)

    score = Column(Float)
    review = Column(Text)

    user = relationship('User')
    book = relationship('Book', back_populates='reviews')
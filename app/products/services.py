from flask_login import current_user

from sqlalchemy import desc, func
from sqlalchemy.orm import joinedload

from app.database import session_scope

from app.products.models import Book, Review, Genre, Stock
from config import BOOK_CATEGORIES

"""
Python file for product(products) supporting functions
"""


def book_to_dict(book) -> dict:
    """Convert book query into a dict for UI"""

    return {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': book.price,
        'cover': book.cover,
        'rating': book.rating,
        'year': book.year,
        'description': book.description,

        'genres': [g.name for g in book.genres]
    }


def review_to_dict(item):
    """Convert Review query into dict for UI"""

    return {
        'id': item.id,
        'book_id': item.book_id,
        'user_id': item.user_id,
        'username': item.user.username if hasattr(item, 'auth') else 'Anonymous',
        'score': item.score,
        'review': item.review,
        'created_at': item.created_at
    }

def format_top_books(raw_books):
    """Convert top products to dict"""
    return [book_to_dict(b) for b in raw_books]


def filter_books_by_category(session, category:str):
    """
    Returns Query with products from selected category
    If category == 'All', returns all the products
    """
    books_query = session.query(Book).options(joinedload(Book.genres))

    if not category or category == 'All':
        return books_query

    genres_in_category = BOOK_CATEGORIES.get(category, [])
    if genres_in_category:
        books_query = books_query.join(Book.genres).filter(Genre.name.in_(genres_in_category))

    return books_query

def filter_books_by_genre(query, genre_name:str):
    """
    Returns products filtered by selected genre
    """
    if genre_name:
        query = query.join(Book.genres).filter(Genre.name == genre_name)
    return query


def check_stock(db_session, book_id:int) -> int:
    """
    Function to check how many products are in stock
    :returns quantity of products in stock
    """
    stock = (db_session.query(Stock)
            .filter_by(book_id=book_id).first())

    return stock.quantity if stock else 0


def get_book(db_session, book_id:int) -> dict:
    """
    Get book information in dict format from database. Used for UI
    """
    book_obj = (
        db_session.query(Book)
        .options(joinedload(Book.genres))
        .filter(Book.id == book_id)
        .first()
    )
    book = book_to_dict(book_obj)

    return book

def get_reviews(db_session, book_id) -> list[dict]:
    """Get list of reviews in dict format from database. Used for UI"""

    reviews_obj = (
        db_session.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.book_id == book_id)
        .order_by(Review.created_at.desc())
        .all()
    )

    return [review_to_dict(r) for r in reviews_obj]

def add_review_score(db_session, book_id: int, user_id: int, score: float, review_text: str | None = None):
    """Add review to database and update the book's rating"""

    review = Review(
        user_id=user_id,
        book_id=book_id,
        score=score,
        review=review_text
    )
    db_session.add(review)
    db_session.flush()

    recalculate_rating(db_session, book_id, score)

    db_session.commit()


def recalculate_rating(db_session, book_id: int, new_score: float):
    """
    Recalculate book rating based on new reviews.
    :param db_session: database session
    :param book_id
    :param new_score: score from a new review
    """
    book = db_session.query(Book).filter(Book.id == book_id).first()

    if book.rating is None:
        book.rating = new_score
        book.rating_count = 1
    else:
        total_score = book.rating * book.rating_count
        total_score += new_score
        book.rating_count += 1
        book.rating = total_score / book.rating_count


def check_existing_review(book_id: int) -> dict|None:
    """
    Check if review is there is an existing review with current book_id  for current_user
    """
    with session_scope() as db_session:
        existing_review = db_session.query(Review).filter_by(
            book_id=book_id,
            user_id=current_user.id
        ).first()

    return existing_review


def search_books(db_session, query: str) -> list[dict]:
    """
    Search products by title or author
    :param db_session: db session
    :param query: string typed by auth
    :return: list of dicts with filtered products
    """
    search_term = f"%{query}%"
    books = (
        db_session.query(Book)
        .filter(
            (Book.title.ilike(search_term)) |
            (Book.author.ilike(search_term))
        )
        .all()
    )
    return [book_to_dict(book) for book in books]



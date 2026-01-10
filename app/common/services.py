"""
Python file for supporting functions shared by several modules
"""

def book_to_dict(book) -> dict:
    """
    Converts book to dictionary
    """
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

def cart_item_to_dict(item, quantity=None) -> dict:
    """
    Convert cart query into a dict for UI
    :param item: CartItem (auth) или Book (guest)
    :param quantity: book quantity
    """
    book = item.book if hasattr(item, 'book') else item
    q = item.quantity if hasattr(item, 'quantity') else quantity

    return {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'price': book.price,
        'cover': book.cover,
        'quantity': q,
        'total': book.price * q
    }


def order_item_to_dict(item) -> dict:
    """Convert OrderItem query into dict for UI"""

    return {
        'id': item.book.id,
        'title': item.book.title,
        'author': item.book.author,
        'price': item.book.price,
        'cover': item.book.cover,
        'quantity': item.quantity,
        'total': item.book.price * item.quantity
    }

def order_to_dict(order) -> dict:
    """Convert Order query into dict for UI"""

    return {
        'id': order.id,
        'created_at': order.date,
        'status': order.status,
        'total_price': sum(
            item.quantity * item.book.price for item in order.items
        ),
        'items': [order_item_to_dict(item) for item in order.items]
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


from flask_login import current_user
from flask import session as flask_session
from app.order.models import CartItem

def get_cart_quantity_guest(book_id: int) -> int:
    """Check if book is already in cart for unauthorized users"""
    cart = flask_session.get('cart', {})
    return cart.get(str(book_id), 0)


def get_cart_quantity_auth(db_session, book_id: int) -> int:
    """Check if book is already in cart for authorized users"""

    cart_item = (
        db_session.query(CartItem)
        .filter_by(user_id=current_user.id, book_id=book_id)
        .first()
    )
    return cart_item.quantity if cart_item else 0

from flask import flash
from flask_login import current_user
from flask import session as flask_session
from sqlalchemy import func, desc

from sqlalchemy.orm import joinedload

from app.database import session_scope

from app.order.models import Order, OrderItem, CartItem
from app.products.models import Book, Stock

from datetime import datetime

"""
Python file for order and cart supporting functions
"""

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


def update_cart_guest(book_id: int, stock: int, change: int) -> bool:
    """Update cart for unathorized users"""

    cart = flask_session.get('cart', {})
    book_id_str = str(book_id)
    current_qty = cart.get(book_id_str, 0)

    new_qty, success = increase_or_decrease_quantity(current_qty, change, stock)
    if not success:
        flash("Out of stock", "warning")
        return False
    elif new_qty == 0:
        cart.pop(book_id_str, None)
    else:
        cart[book_id_str] = new_qty

    flask_session['cart'] = cart
    return True

def update_cart_quantity(book_id: int, change: int) -> bool:
    """Update quantity of products in cart by {change} number"""

    with session_scope() as session:
        book = session.query(Book).get(book_id)
        if not book:
            flash("Книга не найдена", "error")
            return False

        stock = check_stock(session, book_id)

        if current_user.is_authenticated:
            return update_cart_auth(session, book_id, stock, change)
        else:
            return update_cart_guest(book_id, stock, change)


def update_cart_auth(session, book_id: int, stock: int, change: int) -> bool:
    """Update quantity of products in cart by {change} number for authorized users"""

    user_id = current_user.id
    cart_item = session.query(CartItem).filter_by(user_id=user_id, book_id=book_id).first()

    if cart_item:
        new_qty, success = increase_or_decrease_quantity(cart_item.quantity, change, stock)
        if not success:
            flash("Out of stock", "warning")
            return False
        elif new_qty == 0:
            session.delete(cart_item)
            return True
        else:
            cart_item.quantity = new_qty
            return True
    else:
        if change > 0:
            session.add(CartItem(user_id=user_id, book_id=book_id, quantity=min(change, stock)))
            return True
        else:
            return False


def increase_or_decrease_quantity(current_qty: int, change: int, stock: int) -> tuple[int, bool]:
    """
    Increase/descrease quantity of an item
    :param current_qty: current quantity of products
    :param change: number we increase/decrease with
    :param stock: current number of items in stock

    :returns tuple(new_qty, success)
    success=False is stock is exceeded
    """
    new_qty = current_qty + change
    if new_qty > stock:
        return current_qty, False
    elif new_qty <= 0:
        return 0, True
    else:
        return new_qty, True


def get_cart_items(db_session):
    """Get cart items"""

    if current_user.is_authenticated:
        return get_cart_items_auth(db_session)
    else:
        return get_cart_items_session(db_session)


def calculate_total_price(cart_items, selected_ids=None) -> float|int:
    """
    Calculate total price in cart
    :param cart_items: list of dicts from cart_item_to_dict
    :param selected_ids: list of selected products
    """
    total = 0
    for item in cart_items:
        if not selected_ids or item['id'] in selected_ids:
            total += item['quantity'] * item['price']
    return total


def add_address(address_form):
    """Add delivery address depending on selected delivery method"""

    if flask_session.get('delivery_method') == 'store_pickup':
        value = address_form.store_address.data
        store_name, street, city = value.split('|')
        flask_session['address'] = f"{store_name}, {street}, {city}"

    else:
        flask_session[
            'address'] = (f"{address_form.street.data}, "
                          f"{address_form.house.data}, "
                          f"{address_form.apartment.data}, "
                          f"{address_form.city.data}, "
                          f"{address_form.postal_code.data}")




def get_cart_items_auth(db_session) -> list[dict]:
    """
    Get cart items for authorized users
    :param db_session: database session
    :return: list of item dictionary
    """

    items = (
        db_session.query(CartItem)
        .options(joinedload(CartItem.book))
        .filter(CartItem.user_id == current_user.id)
        .all()
    )
    return [cart_item_to_dict(item, db_session) for item in items]


def get_cart_items_session(db_session) -> list[dict]:
    """
    Function to get cart items for unauthorized users
    :param db_session: db session
    :return: list of item dictionary
    """
    cart = flask_session.get('cart', {})
    if not cart:
        return []

    books = db_session.query(Book).filter(Book.id.in_(cart.keys())).all()
    book_map = {b.id: b for b in books}

    items = []
    for book_id_str, quantity in cart.items():
        book = book_map.get(int(book_id_str))
        if book:
            items.append(cart_item_to_dict(book, quantity=quantity))
    return items

def clear_cart():
    """Remove all the items from cart table in db and flask session"""
    if current_user.is_authenticated:
        with session_scope() as session:
            session.query(CartItem).filter(
                CartItem.user_id == current_user.id
            ).delete()
    else:
        flask_session.pop('cart', None)


def create_new_order(cart_items):
    """
    Create new order from cart items
    :param cart_items: products from cart
    :return: order added to database
    """
    order = Order(
        user_id=current_user.id,
        date=datetime.now(),
        status='active',
        address=flask_session.get('address', '')
    )
    with session_scope() as db_session:
        db_session.add(order)
        db_session.flush()

        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=item['id'],
                quantity=item['quantity'],
                price=item['price'] * item['quantity']
            )
            db_session.add(order_item)

            stock = db_session.query(Stock).filter_by(book_id=item['id']).first()
            if stock:
                stock.quantity = max(0, stock.quantity - item['quantity'])

    return order


def get_orders(db_session, status: str | None = None) -> list[dict]:
    """
    Get orders and their status in dict format. Used for UI
    """
    query = (
        db_session.query(Order)
        .options(
            joinedload(Order.items)
            .joinedload(OrderItem.book)
        )
        .filter(Order.user_id == current_user.id)
        .order_by(Order.date.desc())
    )

    if status:
        query = query.filter(Order.status == status)

    orders = query.all()
    return [order_to_dict(order) for order in orders]

def update_order_status(db_session, order_id: int, new_status: str):
    """Update order status: pending -> active, active -> complete"""

    order = db_session.query(Order).filter_by(id=order_id, user_id=current_user.id).first()
    order.status = new_status
    db_session.commit()

def delete_order(db_session, order_id):
    """Delete pending order"""
    order = db_session.query(Order).filter_by(id=order_id, user_id=current_user.id).first()
    db_session.delete(order)
    db_session.commit()


def book_to_dict(book) -> dict:
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

def get_top_books() -> list[dict]:
    """
    Get top 3 products for home page. Ranks products by sales -> by rating
    """

    with session_scope() as db_session:
        sales_subquery = (
            db_session.query(
                OrderItem.book_id,
                func.sum(OrderItem.quantity).label('sales_count')
            )
            .group_by(OrderItem.book_id)
            .subquery()
        )

        top_books_raw = (
            db_session.query(Book)
            .options(
                joinedload(Book.genres),
                joinedload(Book.stock)
            )
            .join(Stock, Stock.book_id == Book.id)
            .outerjoin(sales_subquery, Book.id == sales_subquery.c.book_id)
            .filter(Stock.quantity > 0)
            .order_by(
                desc(sales_subquery.c.sales_count),
                desc(Book.rating)
            )
            .limit(3)
            .all()
        )

        return [book_to_dict(b) for b in top_books_raw]



def check_stock(db_session, book_id:int) -> int:
    """
    Function to check how many products are in stock for order
    :returns quantity of products in stock
    """
    stock = (db_session.query(Stock)
            .filter_by(book_id=book_id).first())

    return stock.quantity if stock else 0

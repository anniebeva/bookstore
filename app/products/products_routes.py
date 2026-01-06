from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from config import BOOK_CATEGORIES

from app.database import session_scope
from . import products_blueprint
from app.products.forms import ReviewForm

from app.products.services import book_to_dict, search_books, \
    filter_books_by_category, filter_books_by_genre, get_book, \
    check_stock, get_reviews, check_existing_review, add_review_score, format_top_books


@products_blueprint.route('/')
@products_blueprint.route('/home')
def home():
    """Home page: top 3 products of the week, categories"""

    categories = list(BOOK_CATEGORIES.keys())

    from app.order.services import get_top_books
    top_books = get_top_books()

    return render_template(
        'products/home.html',
        top_books=top_books,
        categories=categories
    )

@products_blueprint.route('/search')
def search():
    """Search page: filters catalog by requested author/title"""

    query = request.args.get('q', '').strip()
    books = []

    if query:
        with session_scope() as db_session:
            books = search_books(db_session, query)

    return render_template('products/catalog.html',
                           books=books,
                           query=query)


@products_blueprint.route('/catalogue', defaults={'category': None}, methods=['GET', 'POST'])
@products_blueprint.route('/catalogue/<category>', methods=['GET', 'POST'])
def catalog(category):
    """Catalog page: filters products by category and genre"""

    selected_genre = request.args.get('genre')

    with session_scope() as db_session:
        books_query = filter_books_by_category(db_session, category)
        books_query = filter_books_by_genre(books_query, selected_genre)

        books_raw = books_query.all()
        books = [book_to_dict(b) for b in books_raw]

    categories = list(BOOK_CATEGORIES.keys())
    current_category = category or 'All'

    if category == 'All':
        genres_in_category = list({g for gs in BOOK_CATEGORIES.values() for g in gs})
    else:
        genres_in_category = BOOK_CATEGORIES.get(category, [])

    return render_template(
        'products/catalog.html',
        categories=categories,
        current_category=current_category,
        genres=genres_in_category,
        current_genre=selected_genre,
        books=books
    )


@products_blueprint.route('/book_info')
@products_blueprint.route('/book_info/<int:book_id>')
def book_info(book_id:int):
    """Book info page: shows information about book"""

    with session_scope() as db_session:

        book = get_book(db_session, book_id)
        stock = check_stock(db_session, book_id)
        reviews = get_reviews(db_session, book_id)

        if stock == 0:
            flash('No copies available now. Please, try later', 'danger')
            available = False
        else:
            available = True

        from app.order.services import get_cart_quantity_guest, get_cart_quantity_auth
        if current_user.is_authenticated:
            qty_in_cart = get_cart_quantity_auth(db_session, book_id)
        else:
            qty_in_cart = get_cart_quantity_guest(book_id)

    return render_template('products/book_info.html',
                           book=book,
                           qty_in_cart=qty_in_cart,
                           available=available,
                           reviews=reviews)

@products_blueprint.route('/review/<int:book_id>', methods=['GET', 'POST'])
@login_required
def share_review(book_id:int):
    """Review page: share review for a book"""
    existing_review = check_existing_review(book_id)
    if existing_review:
        flash('You have already reviewed this book.', 'danger')
        return redirect(url_for('books_bp.book_info', book_id=book_id))

    review_form = ReviewForm()

    if review_form.validate_on_submit():
        score = review_form.rating.data
        review = review_form.review.data

        with session_scope() as db_session:
            add_review_score(db_session, book_id, current_user.id, score, review)


        flash('Your review has been added!', 'success')
        return redirect(url_for('books_bp.book_info', book_id=book_id))

    elif review_form.errors:
        flash(review_form.errors, category='danger')

    return render_template('products/review.html',
                           review_form=review_form,
                           book_id=book_id)

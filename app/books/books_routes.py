from flask_wtf import FlaskForm
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import TextAreaField, SubmitField
from wtforms.validators import Length, DataRequired

from config import BOOK_CATEGORIES
from . import books_blueprint

from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required

from app.database import session_scope

from app.utils import book_to_dict, get_top_books, search_books, \
    filter_books_by_category, filter_books_by_genre, get_book, \
    check_stock, get_reviews,check_existing_review, add_review_score, get_cart_quantity_auth, \
    get_cart_quantity_guest


class ReviewForm(FlaskForm):
    review = TextAreaField(
        'Review',
        validators=[Length(max=1000)],
        render_kw={'rows': 4}
    )

    rating = RadioField(
        'Rating',
        choices=[
            ('1', '⭐'),
            ('2', '⭐⭐'),
            ('3', '⭐⭐⭐'),
            ('4', '⭐⭐⭐⭐'),
            ('5', '⭐⭐⭐⭐⭐'),
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Submit review')


@books_blueprint.route('/')
@books_blueprint.route('/home')
def home():
    """Home page: top 3 books of the week, categories"""

    categories = list(BOOK_CATEGORIES.keys())
    top_books = get_top_books()

    return render_template(
        'books/home.html',
        top_books=top_books,
        categories=categories
    )

@books_blueprint.route('/search')
def search():
    """Search page: filters catalog by requested author/title"""

    query = request.args.get('q', '').strip()
    books = []

    if query:
        with session_scope() as db_session:
            books = search_books(db_session, query)

    return render_template('books/catalog.html',
                           books=books,
                           query=query)


@books_blueprint.route('/catalogue', defaults={'category': None}, methods=['GET', 'POST'])
@books_blueprint.route('/catalogue/<category>', methods=['GET', 'POST'])
def catalog(category):
    """Catalog page: filters books by category and genre"""

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
        'books/catalog.html',
        categories=categories,
        current_category=current_category,
        genres=genres_in_category,
        current_genre=selected_genre,
        books=books
    )


@books_blueprint.route('/book_info')
@books_blueprint.route('/book_info/<int:book_id>')
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

        if current_user.is_authenticated:
            qty_in_cart = get_cart_quantity_auth(db_session, book_id)
        else:
            qty_in_cart = get_cart_quantity_guest(book_id)

    return render_template('books/book_info.html',
                           book=book,
                           qty_in_cart=qty_in_cart,
                           available=available,
                           reviews=reviews)

@books_blueprint.route('/review/<int:book_id>', methods=['GET', 'POST'])
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

    return render_template('books/review.html',
                           review_form=review_form,
                           book_id=book_id)

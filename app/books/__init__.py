from flask import Blueprint

books_blueprint = Blueprint(
    'books_bp',
    __name__,
    template_folder='templates'
)

from . import books_routes
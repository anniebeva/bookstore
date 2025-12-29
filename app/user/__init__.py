from flask import Blueprint

user_blueprint = Blueprint(
    'user_bp',
    __name__,
    template_folder='templates'
)

from . import user_routes
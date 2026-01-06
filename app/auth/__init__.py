from flask import Blueprint

user_blueprint = Blueprint(
    'auth',
    __name__,
    template_folder='templates'
)

from . import auth_routes
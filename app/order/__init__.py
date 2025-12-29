from flask import Blueprint

order_blueprint = Blueprint(
    'order_bp',
    __name__,
    template_folder='templates'
)

from . import order_routes
from flask import Flask
from flask_login import LoginManager

from config import settings
from app.database import init_db
from app.auth.models import User
from app.database import session_scope

from app.auth.auth_routes import user_blueprint
from app.order.order_routes import order_blueprint
from app.products.products_routes import products_blueprint

app = Flask(__name__)

app.config['SECRET_KEY'] = settings.SECRET_KEY
app.register_blueprint(user_blueprint)
app.register_blueprint(order_blueprint)
app.register_blueprint(products_blueprint)


login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    with session_scope() as session:
        user = session.query(User).get(user_id)
        if user:
            session.expunge(user)

        return user




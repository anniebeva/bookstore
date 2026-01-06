from sqlalchemy import Column, Integer, String
from flask_login import UserMixin
from app.database import Base

class User(Base, UserMixin):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True)
    email = Column(String(120), unique=True)
    phone = Column(String(80), unique=True)
    password_hash = Column(String(256))



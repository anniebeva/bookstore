from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base

from datetime import datetime


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    date = Column(DateTime, default=datetime.utcnow())
    status = Column(String(50), default='new')
    address = Column(String)

    items = relationship('OrderItem',
                         back_populates='order', cascade='all, delete-orphan')

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True)
    order_id = Column(ForeignKey('orders.id'))
    book_id = Column(ForeignKey('products.id'))

    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)

    order = relationship('Order', back_populates='items')
    book = relationship('Book')


class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('users.id'))
    book_id = Column(ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)

    user = relationship('User')
    book = relationship('Book')



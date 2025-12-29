from . import order_blueprint

from flask import flash, redirect, render_template, url_for, request
from flask_login import login_required, current_user
from flask import session as flask_session

from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField
from wtforms.validators import InputRequired

from app.database import session_scope
from app.utils import get_cart_items, calculate_total_price, add_address, update_cart_quantity, \
    create_new_order, clear_cart, get_orders, update_order_status


class DeliveryForm(FlaskForm):
    method = SelectField('Delivery Method', choices=[('store_pickup', 'PickUp from store'),
                                                     ('courier', 'Courier')], validators=[InputRequired()])

class AddressForm(FlaskForm):
    store_address = SelectField('Store', choices=[...])
    street = StringField('Street')
    house = StringField('House')
    apartment = StringField('Apartment')
    city = StringField('City')
    postal_code = StringField('Postal code')

    def validate(self, extra_validators=None):
        if flask_session.get('delivery_method') == 'store_pickup':
            return bool(self.store_address.data)
        else:
            return all([self.street.data, self.house.data, self.city.data, self.postal_code.data])

class PaymentForm(FlaskForm):
    payment_method = RadioField('Payment Method', choices=[('card', 'Card'), ('cash', 'Cash')],
                              validators=[InputRequired()])


@order_blueprint.route('/add_to_cart/<int:book_id>', methods=['POST'])
def add_to_cart(book_id):
    """Add to cart page: add book to cart table or flask session"""

    success = update_cart_quantity(book_id, change=1)
    if success:
        flash("Book added to cart", "success")
    return redirect(request.referrer)


@order_blueprint.route('/cart/remove/<int:book_id>', methods=['POST'])
def remove_copy_from_cart(book_id: int):
    """Remove 1 copy of book from cart table or flask_session"""

    success = update_cart_quantity(book_id, change=-1)
    if success:
        flash("Book removed from cart", "warning")
    return redirect(request.referrer)


@order_blueprint.route('/cart/remove_book/<int:book_id>', methods=['POST'])
def remove_book_from_cart(book_id):
    """Remove all copies of book from cart"""

    update_cart_quantity(book_id, change=-9999)
    flash("Book removed from cart", "warning")
    return redirect(url_for('order_bp.cart'))


@order_blueprint.route('/cart', methods=['GET', 'POST'])
def cart():
    """Cart page: shows all items in cart, total price"""

    with session_scope() as session:
        cart_items = get_cart_items(session)
        total_price = calculate_total_price(cart_items)

    return render_template('order/cart.html',
                           cart_items=cart_items,
                           total_price=total_price)


@order_blueprint.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    """
    Order page:
    delivery, address, payment forms request information about delivery method, address, payment method
    Upon success -> transitions to order_success page
    Processes form requests step by step
    """
    step = request.form.get('step', 'delivery')

    delivery_form = DeliveryForm()
    address_form = AddressForm()
    payment_form = PaymentForm()

    with session_scope() as db_session:
        cart_items = get_cart_items(db_session)
        total_price = calculate_total_price(cart_items)

    if request.method == 'POST':
        if step == 'delivery' and delivery_form.validate_on_submit():
            flask_session['delivery_method'] = delivery_form.method.data
            step = 'address'

        elif step == 'address' and address_form.validate_on_submit():
            add_address(address_form)
            step = 'payment'

        elif step == 'payment' and payment_form.validate_on_submit():

            flask_session['payment_method'] = payment_form.payment_method.data
            step = 'summary'

        elif step == 'summary':
            order = create_new_order(cart_items)

            flask_session['cart_items'] = cart_items
            flask_session['total_price'] = total_price

            if flask_session.get('payment_method') == 'card':
                return redirect(url_for('order_bp.payment_redirect'))

            return redirect(url_for('order_bp.order_success'))

    flask_session['cart_items'] = cart_items
    flask_session['total_price'] = total_price


    return render_template(
            'order/order.html',
            step=step,
            delivery_form=delivery_form,
            address_form=address_form,
            payment_form=payment_form,
            cart_items=cart_items,
            total_price=total_price,
            delivery_method=flask_session.get('delivery_method')
        )


@order_blueprint.route('/payment_redirect', methods=['GET', 'POST'])
@login_required
def payment_redirect():
    """Imitation of payment redirection page: Confirm payment or cancel order"""

    payment_method = flask_session.get('payment_method', 'card')

    if request.method == 'POST':
        return redirect(url_for('order_bp.order_success'))

    return render_template('order/payment_redirect.html', payment_method=payment_method)


@order_blueprint.route('/order/success')
@login_required
def order_success():
    """
    Sucess page: confirms that order was submitted sucessfully
    Function creates new order, decreases  stock, and cleans up cart session and table
    """
    cart_items = flask_session.get('cart_items', [])
    total_price = flask_session.get('total_price', 0)

    if not cart_items:
        flash('No order found', 'warning')
        return redirect(url_for('order_bp.cart'))

    order = create_new_order(cart_items)

    clear_cart()

    flask_session.pop('cart_items', None)
    flask_session.pop('total_price', None)
    flask_session.pop('address', None)
    flask_session.pop('payment_method', None)
    flask_session.pop('delivery_method', None)

    return render_template(
        'order/order_success.html',
        cart_items=cart_items,
        total_price=total_price,
        order=order
    )

@order_blueprint.route('/order_history', methods=['GET', 'POST'])
@login_required
def order_history():
    """Order history page: shows all past orders, sorts them by active and complete"""

    with session_scope() as db_session:
        active_orders = get_orders(db_session, status='active')
        complete_orders = get_orders(db_session, status='complete')

        if request.method == 'POST':
            order_id = request.form.get('order_id')
            if order_id:
                update_order_status(db_session, order_id)
                active_orders = get_orders(db_session, status='active')
                complete_orders = get_orders(db_session, status='complete')

                flash('Enjoy your order! Don\'t forget to share your reviews', 'success')

                return render_template('order/order_history.html',
                    active_orders=active_orders,
                    complete_orders=complete_orders)

    return render_template('order/order_history.html',
                    active_orders=active_orders,
                    complete_orders=complete_orders)



from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectField
from wtforms.validators import InputRequired, DataRequired

from flask import session as flask_session
from config import PICKUP_STORES

class DeliveryForm(FlaskForm):
    method = SelectField('Delivery Method', choices=[('store_pickup', 'PickUp from store'),
                                                     ('courier', 'Courier')], validators=[InputRequired()])

class AddressForm(FlaskForm):
    store_address = SelectField(
        'Pickup location',
        choices=PICKUP_STORES)

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


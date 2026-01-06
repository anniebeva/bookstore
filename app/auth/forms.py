from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(8, 36)])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(4,100)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = StringField('Phone', validators=[InputRequired(), Length(11, 20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(8, 36)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo("password")])

class VerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[InputRequired(), Length(4)])

class EditForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    phone = StringField('Phone', validators=[InputRequired(), Length(11, 20)])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Password', validators=[InputRequired(), Length(8, 36)])
    new_password = PasswordField('Password', validators=[InputRequired(), Length(8, 36)])
    confirm_new_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo("password")])


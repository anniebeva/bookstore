from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required, login_user, logout_user

from app.database import session_scope
from app.auth.models import User
from app.auth.forms import RegistrationForm, VerificationForm, ChangePasswordForm, EditForm, LoginForm

from werkzeug.security import generate_password_hash, check_password_hash

from . import user_blueprint


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """Register page: User registration form"""

    form = RegistrationForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            flash('User with this email already exists!', category='danger')
            return  render_template('auth/register.html', form=form)

        user = User(username=form.username.data,
                    email=form.email.data,
                    phone=form.phone.data,
                    password_hash=generate_password_hash(form.password.data))

        with session_scope() as session:
            session.add(user)

        flash('Registration successful! Please verify your phone.', 'success')
        return redirect(url_for('auth.verify_phone'))

    elif form.errors:
        flash(form.errors, category='danger')

    return render_template('auth/register.html',
                           form=form)


@user_blueprint.route('/verification/phone', methods=['GET', 'POST'])
def verify_phone():
    """Phone verification page. Imitates sms verification process( currently accepts any 6-digit code) """
    form = VerificationForm()

    phone_verification = True
    message_sent = False

    if request.method == 'POST':
        if 'code' not in request.form:
            message_sent = True
            flash('Verification code has been sent to your phone.', 'info')
        else:
            flash('Your phone number has been successfully verified.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/verification.html',
                           user=current_user,
                           message_sent=message_sent,
                           form=form,
                           phone_verification=phone_verification
                           )

@user_blueprint.route('/verification/email', methods=['GET', 'POST'])
def verify_email():
    """Email verification - not used in current V"""

    form = VerificationForm()
    email_verification = True
    message_sent = False
    if request.method == 'POST':
        if 'code' not in request.form:
            message_sent = True
            flash('Verification code has been sent to your email.', 'info')
        else:
            flash('Your email has been successfully verified.', 'success')
            return redirect(url_for('auth.account'))

    return render_template('auth/verification.html',
                           user=current_user,
                           message_sent=message_sent,
                           form=form,
                           email_verification=email_verification
                           )

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """Login page: login to account"""

    form = LoginForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
            if not user:
                flash('No account found with this email. Please register first.','warning')
                return redirect(url_for('auth.register'))

            if not check_password_hash(user.password_hash, form.password.data):
                flash('Incorrect password. Please try again.','danger')
                return render_template('auth/login.html', form=form)

            login_user(user)
            flash('You are successfully logged in!', 'success')
            return redirect(url_for('products.home'))

    return render_template('auth/login.html', form=form)


@user_blueprint.route('/logout')
def logout():
    """Log out from account"""
    logout_user()
    return redirect(url_for('auth.login'))

@user_blueprint.route('/account')
@login_required
def account():
    """Account page: shows auth information"""
    user = current_user
    return render_template('auth/account.html',
                           user=user)


@user_blueprint.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_account():
    """Edit account page: allows auth to edit email and phone number"""
    form = EditForm()
    password_form = ChangePasswordForm()
    user = current_user

    if form.validate_on_submit():
        user.email = form.email.data
        user.phone = form.phone.data

        with session_scope() as session:
            session.add(user)

        flash('Update successful!', 'success')
        return redirect(url_for('auth.account'))

    return render_template('auth/edit_account.html',
                           user=user,
                           form=form,
                           password_form=password_form)


@user_blueprint.route('/account/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page: allows auth to edit password"""
    password_form = ChangePasswordForm()
    user = current_user

    if password_form.validate_on_submit():
        current_pw = password_form.current_password.data
        new_pw = password_form.new_password.data
        confirm_pw = password_form.confirm_new_password.data

        if not check_password_hash(user.password_hash, current_pw):
            flash('Current password is incorrect.', 'danger')
        elif new_pw != confirm_pw:
            flash('New password and confirmation do not match.', 'danger')
        else:
            user.password_hash = generate_password_hash(new_pw)
            with session_scope() as session:
                session.add(user)
            flash('Password successfully changed!', 'success')
            return redirect(url_for('auth.verify_phone',
                                    next=url_for('auth.account')))

    return render_template('auth/edit_account.html', user=user,
                           password_form=password_form, change_password=True)
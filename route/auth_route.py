from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from functools import wraps

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_login import login_user, logout_user, login_required, current_user
from model.entity.user import User
from service.auth_service import AuthService
from model.repository.user_repository import UserRepository

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

auth_service = AuthService()


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField('Confirm', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        old = form.old_password.data
        new = form.new_password.data
        user = current_user
        res = auth_service.verify_password(old, user.hash_password)
        if isinstance(res, tuple):
            verified = bool(res[0])
        else:
            verified = bool(res)
        if not verified:
            flash('Current password incorrect', 'error')
            return render_template('user/change_password.html', form=form), 400
        auth_service.change_password(user, new)
        flash('Password changed successfully', 'success')
        return redirect(url_for('main.index'))
    return render_template('user/change_password.html', form=form)

user_repo = UserRepository()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user: User = user_repo.find_by_email(form.email.data)  # adapt to your repo/service call
    
        if user and auth_service.verify_password(form.password.data, user.hash_password):
            login_user(user)
            flash('Signed in successfully', 'success')
            next_page = request.args.get('next') or url_for('main.index')
            return redirect(next_page)
        # on failure: flash AND render the login page so message is visible there
        flash('Invalid email or password', 'error')
        return render_template('user/login.html', form=form)
    
    return render_template('user/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            auth_service.register_user(email=form.email.data, password=form.password.data)
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('user/register.html', form=form)


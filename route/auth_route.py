from flask import Blueprint, render_template, request, redirect, url_for, flash


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_login import login_user, logout_user, login_required, current_user
from model.dto.user import UserDTO
from model.entity.user import User
from model.repository.user_repository import UserRepository
from service.auth_service import AuthService

auth_service = AuthService()

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


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

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

user_repo = UserRepository()

@login_required
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
        
        auth_service.change_password_dto(user, new)
        flash('Password changed successfully', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('user/change_password.html', form=form)

user_repo = UserRepository()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        userDTO = UserDTO(id=0, email=form.email.data, role='user')
        found_user: User = auth_service.user_repo.find_by_email(userDTO.email)  # adapt to your repo/service call
           
        verified = False
        if found_user:
            res = auth_service.verify_password(form.password.data, found_user.hash_password)
            if isinstance(res, tuple):
                verified = bool(res[0])
            else:
                verified = bool(res)
        
        if not verified:
            flash('Invalid email or password', 'error')
            return render_template('user/login.html', form=form)
        else:
            login_user(found_user)
            flash('Signed in successfully', 'success')
            next_page = request.args.get('next') or url_for('main.index')
            return redirect(next_page)
    
    return render_template('user/login.html', form=form)


@login_required
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
            userDTO = UserDTO(id=0, email=form.email.data, role='user')
            auth_service.register_user_dto(userDTO, password=form.password.data)
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
    return render_template('user/register.html', form=form)


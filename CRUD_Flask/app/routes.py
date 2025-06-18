from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role
from app.forms import LoginForm, UserCreateForm, UserEditForm, ChangePasswordForm
from app.decorators import check_rights

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__, url_prefix='/auth')

@main.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@main.route('/user/<int:id>')
@login_required
def user_view(id):
    user = User.query.get_or_404(id)
    if not current_user.is_admin() and current_user.id != id:
        flash('У вас недостаточно прав для доступа к данной странице.', 'warning')
        return redirect(url_for('main.index'))
    return render_template('user_view.html', user=user)

@main.route('/user/create', methods=['GET', 'POST'])
@login_required
@check_rights('admin')
def user_create():
    form = UserCreateForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            lastname=form.lastname.data,
            firstname=form.firstname.data,
            middlename=form.middlename.data,
            role_id=form.role.data if form.role.data != 0 else None
        )
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Пользователь успешно создан', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при создании пользователя: {str(e)}', 'danger')
    return render_template('user_create.html', form=form)

@main.route('/user/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def user_edit(id):
    user = User.query.get_or_404(id)
    if not current_user.is_admin() and current_user.id != id:
        flash('У вас недостаточно прав для доступа к данной странице.', 'warning')
        return redirect(url_for('main.index'))
    
    form = UserEditForm()
    if not current_user.is_admin():
        del form.role
    
    if request.method == 'GET':
        form.lastname.data = user.lastname
        form.firstname.data = user.firstname
        form.middlename.data = user.middlename
        if current_user.is_admin():
            form.role.data = user.role_id if user.role_id else 0
        
    if form.validate_on_submit():
        user.lastname = form.lastname.data
        user.firstname = form.firstname.data
        user.middlename = form.middlename.data
        if current_user.is_admin() and hasattr(form, 'role'):
            user.role_id = form.role.data if form.role.data != 0 else None
        
        try:
            db.session.commit()
            flash('Пользователь успешно обновлен', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении пользователя: {str(e)}', 'danger')
            
    return render_template('user_edit.html', form=form, user=user)

@main.route('/user/<int:id>/delete', methods=['POST'])
@login_required
@check_rights('admin')
def user_delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Вы не можете удалить свой собственный аккаунт.', 'warning')
        return redirect(url_for('main.index'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Пользователь успешно удален', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')
    return redirect(url_for('main.index'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Неверный текущий пароль', 'danger')
            return render_template('change_password.html', form=form)
            
        current_user.set_password(form.new_password.data)
        try:
            db.session.commit()
            flash('Пароль успешно изменен', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при изменении пароля: {str(e)}', 'danger')
            
    return render_template('change_password.html', form=form)

@main.app_errorhandler(403)
def forbidden(e):
    flash('У вас недостаточно прав для доступа к данной странице.', 'warning')
    return redirect(url_for('main.index'))
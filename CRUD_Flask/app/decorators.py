from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def check_rights(required_role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Пожалуйста, войдите в систему для доступа к этой странице.', 'warning')
                return redirect(url_for('auth.login'))
            
            if required_role == 'admin' and not current_user.is_admin():
                flash('У вас недостаточно прав для доступа к данной странице.', 'warning')
                return redirect(url_for('main.index'))
            
            if required_role == 'self':
                user_id = kwargs.get('user_id')
                if not (current_user.is_admin() or current_user.id == user_id):
                    flash('У вас недостаточно прав для доступа к данной странице.', 'warning')
                    return redirect(url_for('main.index'))
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator
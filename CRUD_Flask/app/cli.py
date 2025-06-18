import click
from flask.cli import with_appcontext
from app import db
from app.models import Role, User

@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('База данных создана.')
    
    admin_role = Role.query.filter_by(name='Администратор').first()
    if not admin_role:
        admin_role = Role(name='Администратор', description='Полный доступ к системе')
        db.session.add(admin_role)
    
    user_role = Role.query.filter_by(name='Пользователь').first()
    if not user_role:
        user_role = Role(name='Пользователь', description='Ограниченный доступ к системе')
        db.session.add(user_role)
    
    if not admin_user:
        admin_user = User(
            username='admin',
            firstname='Администратор',
            lastname='Системы',
            role=admin_role
        )
        admin_user.set_password('admin')
        db.session.add(admin_user)
    
    db.session.commit()
    click.echo('Роли и администратор созданы.')

@click.command('recreate-db')
@with_appcontext
def recreate_db_command():
    db.drop_all()
    db.create_all()
    click.echo('База данных пересоздана.') 
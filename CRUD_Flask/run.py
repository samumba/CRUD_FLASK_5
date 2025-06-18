from app import create_app, db
from app.models import User, Role

app = create_app()

# ✅ Comando para inicializar la base de datos
@app.cli.command('init-db')
def init_db():
    """Создаёт таблицы и роли в базе данных."""
    db.create_all()
    
    if not Role.query.filter_by(name='Администратор').first():
        db.session.add(Role(name='Администратор', description='Полный доступ к системе'))
    
    if not Role.query.filter_by(name='Пользователь').first():
        db.session.add(Role(name='Пользователь', description='Ограниченный доступ к системе'))

    db.session.commit()
    print('✅ База данных инициализирована.')

# ✅ Comando para crear usuario admin
@app.cli.command('create-admin')
def create_admin():
    """Создаёт администратора, если не существует."""
    admin_role = Role.query.filter_by(name='Администратор').first()
    if not admin_role:
        admin_role = Role(name='Администратор', description='Полный доступ к системе')
        db.session.add(admin_role)
        db.session.commit()

    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            firstname='ЭСОНО МАНГЕ',
            lastname='САМУЭЛЬ МБА',
            role_id=admin_role.id
        )
        admin.set_password('Admin123')
        db.session.add(admin)
        db.session.commit()
        print('✅ Администратор создан.')
    else:
        print('ℹ️ Администратор уже существует.')

# ✅ Comando para crear usuario normal
@app.cli.command('create-user')
def create_user():
    """Создаёт обычного пользователя, если не существует."""
    user_role = Role.query.filter_by(name='Пользователь').first()
    if not user_role:
        user_role = Role(name='Пользователь', description='Ограниченный доступ к системе')
        db.session.add(user_role)
        db.session.commit()

    if not User.query.filter_by(username='user').first():
        user = User(
            username='user',
            firstname='ЭСОНО МАНГЕ',
            lastname='МАНУЭЛЬ ЭСОНО',
            middlename='АААА',
            role_id=user_role.id
        )
        user.set_password('User123')
        db.session.add(user)
        db.session.commit()
        print('✅ Пользователь создан.')
    else:
        print('ℹ️ Пользователь уже существует.')

# ✅ Bloque de ejecución normal
if __name__ == '__main__':
    app.run(debug=True)

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from app import db, login_manager

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(256))
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(64))
    firstname = db.Column(db.String(64), nullable=False)
    middlename = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    visits = db.relationship('VisitLog', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        if self.lastname:
            return f"{self.lastname} {self.firstname} {self.middlename or ''}"
        return f"{self.firstname} {self.middlename or ''}"
    
    def is_admin(self):
        return self.role and self.role.name == 'Администратор'
    
    def __repr__(self):
        return f'<User {self.username}>'

class AnonymousUser(AnonymousUserMixin):
    def is_admin(self):
        return False

login_manager.anonymous_user = AnonymousUser

class VisitLog(db.Model):
    __tablename__ = 'visit_log'
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VisitLog {self.path}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError
import re
from app.models import User, Role

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(message='Поле не может быть пустым')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Поле не может быть пустым')])
    submit = SubmitField('Войти')

class UserCreateForm(FlaskForm):
    username = StringField('Логин', validators=[
        DataRequired(message='Поле не может быть пустым'),
        Length(min=5, message='Логин должен быть не менее 5 символов'),
        Regexp('^[A-Za-z0-9]+$', message='Логин должен содержать только латинские буквы и цифры')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Поле не может быть пустым'),
        Length(min=8, max=128, message='Пароль должен быть от 8 до 128 символов')
    ])
    lastname = StringField('Фамилия', validators=[DataRequired(message='Поле не может быть пустым')])
    firstname = StringField('Имя', validators=[DataRequired(message='Поле не может быть пустым')])
    middlename = StringField('Отчество')
    role = SelectField('Роль', coerce=int)
    submit = SubmitField('Сохранить')
    
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.role.choices = [(0, 'Не выбрано')] + [(role.id, role.name) for role in Role.query.all()]
    
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Этот логин уже используется')
    
    def validate_password(self, field):
        password = field.data
        
        if not re.search(r'[A-ZА-Я]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
            
        if not re.search(r'[a-zа-я]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')
            
        if not re.search(r'[0-9]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну цифру')
            
        if re.search(r'\s', password):
            raise ValidationError('Пароль не должен содержать пробелы')
            
        valid_chars = r'A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+()[\]{}><\/\\|"\'\.,;:'
        if not re.match(f'^[{valid_chars}]+$', password):
            raise ValidationError('Пароль содержит недопустимые символы')

class UserEditForm(FlaskForm):
    lastname = StringField('Фамилия', validators=[DataRequired(message='Поле не может быть пустым')])
    firstname = StringField('Имя', validators=[DataRequired(message='Поле не может быть пустым')])
    middlename = StringField('Отчество')
    role = SelectField('Роль', coerce=int)
    submit = SubmitField('Сохранить')
    
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.role.choices = [(0, 'Не выбрано')] + [(role.id, role.name) for role in Role.query.all()]

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired(message='Поле не может быть пустым')])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Поле не может быть пустым'),
        Length(min=8, max=128, message='Пароль должен быть от 8 до 128 символов')
    ])
    confirm_password = PasswordField('Повторите новый пароль', validators=[
        DataRequired(message='Поле не может быть пустым'),
        EqualTo('new_password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Изменить пароль')
    
    def validate_new_password(self, field):
        password = field.data
        
        if not re.search(r'[A-ZА-Я]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву')
            
        if not re.search(r'[a-zа-я]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну строчную букву')
            
        if not re.search(r'[0-9]', password):
            raise ValidationError('Пароль должен содержать хотя бы одну цифру')
            
        if re.search(r'\s', password):
            raise ValidationError('Пароль не должен содержать пробелы')
            
        valid_chars = r'A-Za-zА-Яа-я0-9~!?@#$%^&*_\-+()[\]{}><\/\\|"\'\.,;:'
        if not re.match(f'^[{valid_chars}]+$', password):
            raise ValidationError('Пароль содержит недопустимые символы')
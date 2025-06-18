import csv
import io
from flask import render_template, request, flash, redirect, url_for, make_response
from flask_login import current_user
from sqlalchemy import func
from app import db
from app.models import VisitLog, User
from app.decorators import check_rights
from . import stats

# Количество записей на странице для пагинации
RECORDS_PER_PAGE = 10

@stats.route('/')
@check_rights()
def index():
    page = request.args.get('page', 1, type=int)
    query = VisitLog.query.order_by(VisitLog.created_at.desc())
    
    # Если пользователь не админ, показывать только его записи
    if not current_user.is_admin():
        query = query.filter_by(user_id=current_user.id)
    
    pagination = query.paginate(page=page, per_page=RECORDS_PER_PAGE, error_out=False)
    visits = pagination.items
    
    return render_template('stats/index.html', visits=visits, pagination=pagination)

@stats.route('/pages')
@check_rights()
def pages_report():
    # Запрос для получения статистики по страницам
    query = db.session.query(
        VisitLog.path, 
        func.count(VisitLog.id).label('visits_count')
    )
    
    # Если пользователь не админ, показывать только его статистику
    if not current_user.is_admin():
        query = query.filter_by(user_id=current_user.id)
    
    stats_data = query.group_by(VisitLog.path).order_by(func.count(VisitLog.id).desc()).all()
    
    return render_template('stats/pages_report.html', stats_data=stats_data)

@stats.route('/users')
@check_rights(required_role='admin')
def users_report():
    # Запрос для получения статистики по пользователям
    query = db.session.query(
        User.id,
        func.count(VisitLog.id).label('visits_count')
    ).outerjoin(VisitLog, User.id == VisitLog.user_id).group_by(User.id).order_by(func.count(VisitLog.id).desc())
    
    stats_data = query.all()
    
    # Получение количества посещений неаутентифицированными пользователями
    anon_visits_count = db.session.query(func.count(VisitLog.id)).filter(VisitLog.user_id == None).scalar() or 0
    
    # Передаем объект запроса User.query в шаблон
    return render_template('stats/users_report.html', stats_data=stats_data, anon_visits_count=anon_visits_count, user_query=User.query)

@stats.route('/export/pages')
@check_rights()
def export_pages():
    # Запрос для получения статистики по страницам
    query = db.session.query(
        VisitLog.path, 
        func.count(VisitLog.id).label('visits_count')
    )
    
    # Если пользователь не админ, показывать только его статистику
    if not current_user.is_admin():
        query = query.filter_by(user_id=current_user.id)
    
    stats_data = query.group_by(VisitLog.path).order_by(func.count(VisitLog.id).desc()).all()
    
    # Создание CSV файла
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Запись заголовков
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    
    # Запись данных
    for index, (path, count) in enumerate(stats_data, 1):
        writer.writerow([index, path, count])
    
    # Создание ответа
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=pages_report.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@stats.route('/export/users')
@check_rights(required_role='admin')
def export_users():
    # Запрос для получения статистики по пользователям
    query = db.session.query(
        User.id,
        User.lastname,
        User.firstname,
        User.middlename,
        func.count(VisitLog.id).label('visits_count')
    ).outerjoin(VisitLog, User.id == VisitLog.user_id).group_by(User.id).order_by(func.count(VisitLog.id).desc())
    
    stats_data = query.all()
    
    # Получение количества посещений неаутентифицированными пользователями
    anon_visits_count = db.session.query(func.count(VisitLog.id)).filter(VisitLog.user_id == None).scalar() or 0
    
    # Создание CSV файла
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Запись заголовков
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    
    # Запись данных
    index = 1
    for user_id, lastname, firstname, middlename, count in stats_data:
        full_name = f"{lastname or ''} {firstname or ''} {middlename or ''}".strip()
        writer.writerow([index, full_name, count])
        index += 1
    
    # Добавление неаутентифицированных пользователей
    if anon_visits_count > 0:
        writer.writerow([index, 'Неаутентифицированный пользователь', anon_visits_count])
    
    # Создание ответа
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=users_report.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response
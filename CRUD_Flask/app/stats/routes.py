from flask import render_template, send_file, make_response, request
from flask_login import current_user, login_required
from app.decorators import check_rights
from app.models import VisitLog, User
from app import db
from . import stats
import io
import csv

ITEMS_PER_PAGE = 20

@stats.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = VisitLog.query
    
    if not current_user.is_admin():
        query = query.filter_by(user_id=current_user.id)
    
    logs = query.order_by(VisitLog.created_at.desc()).paginate(
        page=page, per_page=ITEMS_PER_PAGE, error_out=False)
    
    return render_template('stats/index.html', logs=logs)

@stats.route('/by-pages')
@login_required
@check_rights('admin')
def by_pages():
    stats = db.session.query(
        VisitLog.path,
        db.func.count(VisitLog.id).label('visits_count')
    ).group_by(VisitLog.path).order_by(db.text('visits_count DESC')).all()
    
    return render_template('stats/by_pages.html', stats=stats)

@stats.route('/by-users')
@login_required
@check_rights('admin')
def by_users():
    stats = db.session.query(
        User,
        db.func.count(VisitLog.id).label('visits_count')
    ).outerjoin(VisitLog).group_by(User.id).order_by(db.text('visits_count DESC')).all()
    
    return render_template('stats/by_users.html', stats=stats)

@stats.route('/export/pages')
@login_required
@check_rights('admin')
def export_pages():
    stats = db.session.query(
        VisitLog.path,
        db.func.count(VisitLog.id).label('visits_count')
    ).group_by(VisitLog.path).order_by(db.text('visits_count DESC')).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    
    for idx, (path, count) in enumerate(stats, 1):
        writer.writerow([idx, path, count])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='pages_stats.csv'
    )

@stats.route('/export/users')
@login_required
@check_rights('admin')
def export_users():
    stats = db.session.query(
        User,
        db.func.count(VisitLog.id).label('visits_count')
    ).outerjoin(VisitLog).group_by(User.id).order_by(db.text('visits_count DESC')).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    
    for idx, (user, count) in enumerate(stats, 1):
        writer.writerow([idx, user.get_full_name() if user else 'Неаутентифицированный пользователь', count])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='users_stats.csv'
    ) 
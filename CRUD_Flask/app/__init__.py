from flask import Flask, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.routes import main, auth
    from app.stats import stats
    
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(stats)
    
    @app.before_request
    def log_visit():
        if not request.path.startswith('/static/') and request.endpoint:
            from app.models import VisitLog
            user_id = current_user.id if current_user.is_authenticated else None
            log_entry = VisitLog(path=request.path, user_id=user_id)
            db.session.add(log_entry)
            db.session.commit()
    
    from app.cli import init_db_command, recreate_db_command
    app.cli.add_command(init_db_command)
    app.cli.add_command(recreate_db_command)
    
    return app
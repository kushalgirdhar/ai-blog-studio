from flask import Flask
from app.routes import blog
from config import Config
from app.extensions import db, login_manager
from flask_migrate import Migrate
from app.models.user import User
from flask_wtf.csrf import CSRFProtect
from app.models.login_history import LoginHistory
from app.models.blog import BlogPost



migrate = Migrate()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    csrf.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.blog import blog
    app.register_blueprint(blog)

    return app


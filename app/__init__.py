from flask import Flask, app
from .config import Config
from .extensions import db, migrate, cors, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config["SECRET_KEY"] = "dev-change-this-later"

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "web.login"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.web import web_bp
    from .routes.admin_web import admin_web_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(admin_web_bp, url_prefix="/admin")
    from .routes.couples import couples_bp
    from .routes.health import health_bp
    from .routes.home import home_bp
    from .routes.decks import decks_bp
    from .routes.questions import questions_bp
    from .routes.sessions import sessions_bp
    from .routes.favorites import favorites_bp
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.admin import admin_bp
    from .routes.couple_features import couple_features_bp
    
    app.register_blueprint(couple_features_bp, url_prefix="/api/couples")
    app.register_blueprint(couples_bp, url_prefix="/api/couples")

    app.register_blueprint(health_bp)
    app.register_blueprint(home_bp, url_prefix="/api")
    app.register_blueprint(decks_bp, url_prefix="/api/decks")
    app.register_blueprint(questions_bp, url_prefix="/api/questions")
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(favorites_bp, url_prefix="/api/favorites")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    return app

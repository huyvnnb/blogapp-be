from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from pydantic import ValidationError

from blog.database import db
from blog.exception import ApiError
from blog.report.admin.route import admin_stats_bp
from blog.report.route import user_stats_bp
from blog.settings import DevConfig
from blog.utils.response import error

# db = SQLAlchemy()


def create_app(config=DevConfig):
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=["*"])
    JWTManager(app)

    app.config.from_object(config)

    from blog.posts.route import post_bp
    from blog.users.route import user_bp, auth_bp
    from blog.admin.route import admin_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(post_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_stats_bp)
    app.register_blueprint(user_stats_bp)

    # Exception handler
    @app.errorhandler(ApiError)
    def handle_api_error(e):
        return error(e.message, e.status_code)

    @app.errorhandler(404)
    def handle_404(e):
        return error("Not Found", 404)

    @app.errorhandler(ValidationError)
    def handle_validate_error(e):
        return error("Validation error", 422, data=str(e))

    @app.errorhandler(Exception)
    def handle_exception(e):
        return error("Internal Server Error", 500, data=str(e))

    db.init_app(app)
    with app.app_context():
        from blog.users.model import Users
        from blog.posts.model import Posts

        db.create_all()

    return app

# Standard library
from flask import Flask, jsonify

# Third-party
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

# Local modules
from config import Config
from app.extensions import db, jwt, ma
from app.routes.auth import auth_bp
from app.routes.inspection import inspection_bp
from app.models import user, inspection
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            db.create_all()
            print("✅ Database connected successfully.")
        except Exception as e:
            print("❌ Database connection failed:", e)
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(inspection_bp)

    # Global error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500
    
    return app

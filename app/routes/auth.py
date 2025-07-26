from flask import Blueprint, request, jsonify
import re
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import log_request

auth_bp = Blueprint("auth", __name__)

def is_strong_password(pwd):
    return (
        len(pwd) >= 8 and
        re.search(r"[A-Z]", pwd) and
        re.search(r"[a-z]", pwd) and
        re.search(r"[0-9]", pwd) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", pwd)
    )

@auth_bp.route("/signup", methods=["POST"])
def signup():
    log_request(request.path)
    try:
        data = request.json
        if not data.get("username") or not data.get("password"):
            return {"error": "Missing fields"}, 400

        if not is_strong_password(data["password"]):
            return {"error": "Password too weak. Use at least 8 characters with mix of upper, lower, digit, symbol."}, 400
        
        if User.query.filter_by(username=data["username"]).first():
            return {"error": "Username already exists"}, 409

        user = User(username=data["username"])
        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()

        return {"message": "User created"}, 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": "Database error", "details": str(e)}, 500
    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}, 500


@auth_bp.route("/login", methods=["POST"])
def login():
    log_request(request.path)
    try:
        data = request.json
        user = User.query.filter_by(username=data["username"]).first()
        if not user or not user.check_password(data["password"]):
            return {"error": "Invalid credentials"}, 401

        access_token = create_access_token(identity=str(user.id))
        return {"token": access_token}, 200

    except Exception as e:
        return {"error": "Unexpected error", "details": str(e)}, 500

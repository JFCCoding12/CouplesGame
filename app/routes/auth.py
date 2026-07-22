from datetime import datetime, timedelta
import jwt

from flask import Blueprint, request, abort, current_app
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)


def create_token(user):
    payload = {
        "user_id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "exp": datetime.utcnow() + timedelta(days=30),
    }

    return jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}

    email = data.get("email", "").lower().strip()
    password = data.get("password")
    display_name = data.get("display_name", "").strip()

    if not email or not password or not display_name:
        abort(400, description="email, password, and display_name are required.")

    if User.query.filter_by(email=email).first():
        abort(409, description="Email already registered.")

    user = User(
        email=email,
        display_name=display_name,
        is_admin=False,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    token = create_token(user)

    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
        }
    }, 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}

    email = data.get("email", "").lower().strip()
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        abort(401, description="Invalid email or password.")

    token = create_token(user)

    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
        }
    }
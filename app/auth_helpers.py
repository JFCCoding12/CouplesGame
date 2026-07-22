import jwt
from functools import wraps
from flask import request, abort, current_app, g

from app.models import User


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing bearer token.")

        token = auth_header.replace("Bearer ", "").strip()

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            abort(401, description="Token expired.")
        except jwt.InvalidTokenError:
            abort(401, description="Invalid token.")

        user = User.query.get(payload.get("user_id"))

        if not user or not user.is_active:
            abort(401, description="User not found.")

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
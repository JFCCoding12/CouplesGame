from flask import Blueprint, abort

from app.models import User

users_bp = Blueprint("users", __name__)


@users_bp.get("/<int:user_id>")
def get_user(user_id):
    user = User.query.get(user_id)

    if user is None:
        abort(404, description="User not found.")

    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat(),
    }
import secrets
import string

from flask import Blueprint, request, abort, g

from app.extensions import db
from app.auth_helpers import token_required
from app.models import Couple, CoupleMember

couples_bp = Blueprint("couples", __name__)


def generate_invite_code(length=6):
    alphabet = string.ascii_uppercase + string.digits

    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(length))
        if not Couple.query.filter_by(invite_code=code).first():
            return code


def couple_to_dict(couple):
    return {
        "id": couple.id,
        "name": couple.name,
        "invite_code": couple.invite_code,
        "members": [
            {
                "id": member.user.id,
                "display_name": member.user.display_name,
                "email": member.user.email,
                "role": member.role,
            }
            for member in couple.members
        ],
    }


@couples_bp.get("/me")
@token_required
def my_couple():
    membership = CoupleMember.query.filter_by(
        user_id=g.current_user.id
    ).first()

    if not membership:
        return {"couple": None}

    return {"couple": couple_to_dict(membership.couple)}


@couples_bp.post("")
@token_required
def create_couple():
    data = request.get_json() or {}

    existing_membership = CoupleMember.query.filter_by(
        user_id=g.current_user.id
    ).first()

    if existing_membership:
        abort(409, description="User already belongs to a couple.")

    couple = Couple(
        name=data.get("name") or None,
        invite_code=generate_invite_code(),
    )

    db.session.add(couple)
    db.session.flush()

    member = CoupleMember(
        couple_id=couple.id,
        user_id=g.current_user.id,
        role="owner",
    )

    db.session.add(member)
    db.session.commit()

    return couple_to_dict(couple), 201


@couples_bp.post("/join")
@token_required
def join_couple():
    data = request.get_json() or {}

    invite_code = (data.get("invite_code") or "").upper().strip()

    if not invite_code:
        abort(400, description="invite_code is required.")

    existing_membership = CoupleMember.query.filter_by(
        user_id=g.current_user.id
    ).first()

    if existing_membership:
        abort(409, description="User already belongs to a couple.")

    couple = Couple.query.filter_by(invite_code=invite_code).first()

    if not couple:
        abort(404, description="Invalid invite code.")

    member = CoupleMember(
        couple_id=couple.id,
        user_id=g.current_user.id,
        role="member",
    )

    db.session.add(member)
    db.session.commit()

    return couple_to_dict(couple)
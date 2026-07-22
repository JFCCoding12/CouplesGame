from flask import Blueprint, request, abort

from app.extensions import db
from app.models import FavoriteQuestion, Question

favorites_bp = Blueprint("favorites", __name__)


@favorites_bp.get("")
def get_favorites():
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        abort(400, description="user_id is required.")

    favorites = FavoriteQuestion.query.filter_by(user_id=user_id).all()

    return {
        "favorites": [
            {
                "id": favorite.id,
                "question_id": favorite.question_id,
                "question": favorite.question.to_dict() if favorite.question else None,
                "created_at": favorite.created_at.isoformat(),
            }
            for favorite in favorites
        ]
    }


@favorites_bp.post("")
def add_favorite():
    data = request.get_json() or {}

    user_id = data.get("user_id")
    question_id = data.get("question_id")

    if not user_id or not question_id:
        abort(400, description="user_id and question_id are required.")

    question = Question.query.get(question_id)

    if question is None:
        abort(404, description="Question not found.")

    existing = FavoriteQuestion.query.filter_by(
        user_id=user_id,
        question_id=question_id,
    ).first()

    if existing:
        return {"message": "Already favorited."}, 200

    favorite = FavoriteQuestion(
        user_id=user_id,
        question_id=question_id,
    )

    db.session.add(favorite)
    db.session.commit()

    return {
        "id": favorite.id,
        "user_id": favorite.user_id,
        "question_id": favorite.question_id,
        "created_at": favorite.created_at.isoformat(),
    }, 201


@favorites_bp.delete("/<int:question_id>")
def remove_favorite(question_id):
    user_id = request.args.get("user_id", type=int)

    if not user_id:
        abort(400, description="user_id is required.")

    favorite = FavoriteQuestion.query.filter_by(
        user_id=user_id,
        question_id=question_id,
    ).first()

    if favorite is None:
        abort(404, description="Favorite not found.")

    db.session.delete(favorite)
    db.session.commit()

    return {"message": "Favorite removed."}
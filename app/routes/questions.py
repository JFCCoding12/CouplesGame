from flask import Blueprint, request, abort
from sqlalchemy import func

from app.models import Deck, Question

questions_bp = Blueprint("questions", __name__)


@questions_bp.get("")
def get_questions():
    limit = min(int(request.args.get("limit", 20)), 50)
    offset = int(request.args.get("offset", 0))
    deck_id = request.args.get("deck_id")

    query = Question.query.filter_by(is_active=True)

    if deck_id:
        query = query.filter_by(deck_id=deck_id)

    questions = (
        query
        .order_by(Question.sort_order.asc(), Question.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "questions": [q.to_dict() for q in questions],
        "limit": limit,
        "offset": offset,
        "has_more": len(questions) == limit,
    }


@questions_bp.get("/deck/<string:deck_id>")
def get_questions_for_deck(deck_id):
    limit = min(int(request.args.get("limit", 20)), 50)
    offset = int(request.args.get("offset", 0))

    deck = Deck.query.filter_by(id=deck_id, is_active=True).first()

    if deck is None:
        abort(404, description="Deck not found.")

    questions = (
        Question.query
        .filter_by(deck_id=deck_id, is_active=True)
        .order_by(Question.sort_order.asc(), Question.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "deck": deck.to_dict(),
        "questions": [q.to_dict() for q in questions],
        "limit": limit,
        "offset": offset,
        "has_more": len(questions) == limit,
    }


@questions_bp.get("/random")
def random_questions():
    limit = min(int(request.args.get("limit", 20)), 50)
    deck_id = request.args.get("deck_id")

    query = Question.query.filter_by(is_active=True)

    if deck_id:
        query = query.filter_by(deck_id=deck_id)

    questions = query.order_by(func.random()).limit(limit).all()

    return {
        "questions": [q.to_dict() for q in questions],
        "limit": limit,
    }


@questions_bp.get("/<int:question_id>")
def get_question(question_id):
    question = Question.query.filter_by(id=question_id, is_active=True).first()

    if question is None:
        abort(404, description="Question not found.")

    return question.to_dict()
from flask import Blueprint
from sqlalchemy import func

from app.extensions import db
from app.models import Deck, Question

home_bp = Blueprint("home", __name__)


@home_bp.get("/home")
def home():
    decks = (
        Deck.query
        .filter_by(is_active=True)
        .order_by(Deck.sort_order.asc(), Deck.name.asc())
        .all()
    )

    daily_question = (
        Question.query
        .filter_by(is_active=True, is_nsfw=False)
        .order_by(func.random())
        .first()
    )

    return {
        "user": None,
        "stats": {
            "current_streak": 0,
            "questions_answered": 0,
            "longest_streak": 0,
            "favorite_category": None,
        },
        "continue_deck": None,
        "daily_question": daily_question.to_dict() if daily_question else None,
        "decks": [deck.to_dict() for deck in decks],
    }
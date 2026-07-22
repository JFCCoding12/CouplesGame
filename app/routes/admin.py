from functools import wraps

from flask import Blueprint, request, abort

from app.extensions import db
from app.models import Deck, Question, User

admin_bp = Blueprint("admin", __name__)


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # TEMP admin auth until JWT exists.
        # Pass ?admin_user_id=1 or header X-Admin-User-Id: 1
        admin_user_id = request.headers.get("X-Admin-User-Id") or request.args.get("admin_user_id")

        if not admin_user_id:
            abort(401, description="Admin user required.")

        user = User.query.get(int(admin_user_id))

        if not user or not user.is_active or not user.is_admin:
            abort(403, description="Admin access required.")

        return fn(*args, **kwargs)

    return wrapper


# --------------------
# Dashboard
# --------------------

@admin_bp.get("")
@require_admin
def admin_dashboard():
    return {
        "counts": {
            "decks": Deck.query.count(),
            "active_decks": Deck.query.filter_by(is_active=True).count(),
            "questions": Question.query.count(),
            "active_questions": Question.query.filter_by(is_active=True).count(),
            "users": User.query.count(),
        }
    }


# --------------------
# Deck Admin
# --------------------

@admin_bp.get("/decks")
@require_admin
def admin_get_decks():
    decks = Deck.query.order_by(Deck.sort_order.asc(), Deck.name.asc()).all()
    return {"decks": [deck.to_dict() for deck in decks]}


@admin_bp.post("/decks")
@require_admin
def admin_create_deck():
    data = request.get_json() or {}

    required = ["id", "name", "emoji"]
    for field in required:
        if not data.get(field):
            abort(400, description=f"{field} is required.")

    existing = Deck.query.get(data["id"])
    if existing:
        abort(409, description="Deck already exists.")

    deck = Deck(
        id=data["id"],
        name=data["name"],
        emoji=data["emoji"],
        primary_color=data.get("primary_color", "#EC4899"),
        secondary_color=data.get("secondary_color"),
        description=data.get("description") or None,
        is_nsfw=bool(data.get("is_nsfw", False)),
        is_active=bool(data.get("is_active", True)),
        sort_order=int(data.get("sort_order", 0)),
    )

    db.session.add(deck)
    db.session.commit()

    return deck.to_dict(), 201


@admin_bp.put("/decks/<string:deck_id>")
@require_admin
def admin_update_deck(deck_id):
    deck = Deck.query.get(deck_id)

    if not deck:
        abort(404, description="Deck not found.")

    data = request.get_json() or {}

    deck.name = data.get("name", deck.name)
    deck.emoji = data.get("emoji", deck.emoji)
    deck.primary_color = data.get("primary_color", deck.primary_color)
    deck.secondary_color = data.get("secondary_color", deck.secondary_color)
    deck.description = data.get("description", deck.description) or None

    if "is_nsfw" in data:
        deck.is_nsfw = bool(data["is_nsfw"])

    if "is_active" in data:
        deck.is_active = bool(data["is_active"])

    if "sort_order" in data:
        deck.sort_order = int(data["sort_order"])

    db.session.commit()

    return deck.to_dict()


@admin_bp.delete("/decks/<string:deck_id>")
@require_admin
def admin_archive_deck(deck_id):
    deck = Deck.query.get(deck_id)

    if not deck:
        abort(404, description="Deck not found.")

    deck.is_active = False
    db.session.commit()

    return {"message": "Deck archived.", "deck": deck.to_dict()}


# --------------------
# Question Admin
# --------------------

@admin_bp.get("/questions")
@require_admin
def admin_get_questions():
    deck_id = request.args.get("deck_id")
    active_only = request.args.get("active_only", "false").lower() == "true"

    query = Question.query

    if deck_id:
        query = query.filter_by(deck_id=deck_id)

    if active_only:
        query = query.filter_by(is_active=True)

    questions = (
        query
        .order_by(Question.deck_id.asc(), Question.sort_order.asc(), Question.id.asc())
        .all()
    )

    return {"questions": [q.to_dict() for q in questions]}


@admin_bp.post("/questions")
@require_admin
def admin_create_question():
    data = request.get_json() or {}

    if not data.get("deck_id"):
        abort(400, description="deck_id is required.")

    if not data.get("text"):
        abort(400, description="text is required.")

    deck = Deck.query.get(data["deck_id"])
    if not deck:
        abort(404, description="Deck not found.")

    question = Question(
        deck_id=data["deck_id"],
        text=data["text"],
        level=data.get("level", "general"),
        tags=data.get("tags", []),
        is_active=bool(data.get("is_active", True)),
        is_nsfw=bool(data.get("is_nsfw", False)),
        sort_order=int(data.get("sort_order", 0)),
    )

    db.session.add(question)
    db.session.commit()

    return question.to_dict(), 201


@admin_bp.put("/questions/<int:question_id>")
@require_admin
def admin_update_question(question_id):
    question = Question.query.get(question_id)

    if not question:
        abort(404, description="Question not found.")

    data = request.get_json() or {}

    if "deck_id" in data:
        deck = Deck.query.get(data["deck_id"])
        if not deck:
            abort(404, description="Deck not found.")
        question.deck_id = data["deck_id"]

    question.text = data.get("text", question.text)
    question.level = data.get("level", question.level)
    question.tags = data.get("tags", question.tags)

    if "is_active" in data:
        question.is_active = bool(data["is_active"])

    if "is_nsfw" in data:
        question.is_nsfw = bool(data["is_nsfw"])

    if "sort_order" in data:
        question.sort_order = int(data["sort_order"])

    db.session.commit()

    return question.to_dict()


@admin_bp.delete("/questions/<int:question_id>")
@require_admin
def admin_archive_question(question_id):
    question = Question.query.get(question_id)

    if not question:
        abort(404, description="Question not found.")

    question.is_active = False
    db.session.commit()

    return {"message": "Question archived.", "question": question.to_dict()}


# --------------------
# Bulk Import
# --------------------

@admin_bp.post("/questions/bulk")
@require_admin
def admin_bulk_create_questions():
    data = request.get_json() or {}

    deck_id = data.get("deck_id")
    questions = data.get("questions", [])

    if not deck_id:
        abort(400, description="deck_id is required.")

    deck = Deck.query.get(deck_id)
    if not deck:
        abort(404, description="Deck not found.")

    if not isinstance(questions, list) or not questions:
        abort(400, description="questions must be a non-empty list.")

    created = []

    for index, item in enumerate(questions):
        if isinstance(item, str):
            text = item.strip()
            level = "general"
            tags = []
            is_nsfw = False
        else:
            text = item.get("text", "").strip()
            level = item.get("level", "general")
            tags = item.get("tags", [])
            is_nsfw = bool(item.get("is_nsfw", False))

        if not text:
            continue

        question = Question(
            deck_id=deck_id,
            text=text,
            level=level,
            tags=tags,
            is_nsfw=is_nsfw,
            sort_order=index,
        )

        db.session.add(question)
        created.append(question)

    db.session.commit()

    return {
        "created_count": len(created),
        "questions": [q.to_dict() for q in created],
    }, 201
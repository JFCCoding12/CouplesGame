from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import current_user, login_required
from app.extensions import db
from app.models import Deck, Question
import json

admin_web_bp = Blueprint("admin_web", __name__)

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@admin_web_bp.get("/")
@admin_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        deck_count=Deck.query.count(),
        question_count=Question.query.count()
    )

@admin_web_bp.get("/decks")
@admin_required
def decks():
    decks = Deck.query.order_by(Deck.sort_order, Deck.name).all()
    return render_template("admin/decks.html", decks=decks)

@admin_web_bp.get("/decks/new")
@admin_required
def new_deck():
    return render_template("admin/deck_form.html", deck=None)

@admin_web_bp.post("/decks/new")
@admin_required
def create_deck():
    deck = Deck(
        id=request.form["id"],
        name=request.form["name"],
        emoji=request.form["emoji"],
        primary_color=request.form.get("primary_color") or "#314755",
        secondary_color=request.form.get("secondary_color") or "#26A0DA",
        description=request.form.get("description") or None,
        sort_order=int(request.form.get("sort_order") or 0),
        is_nsfw=bool(request.form.get("is_nsfw")),
        is_active=True
    )

    db.session.add(deck)
    db.session.commit()

    return redirect(url_for("admin_web.decks"))

@admin_web_bp.get("/decks/<string:deck_id>/edit")
@admin_required
def edit_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    return render_template("admin/deck_form.html", deck=deck)

@admin_web_bp.post("/decks/<string:deck_id>/edit")
@admin_required
def update_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)

    deck.name = request.form["name"]
    deck.emoji = request.form["emoji"]
    deck.primary_color = request.form.get("primary_color") or "#314755"
    deck.secondary_color = request.form.get("secondary_color") or "#26A0DA"
    deck.description = request.form.get("description") or None
    deck.sort_order = int(request.form.get("sort_order") or 0)
    deck.is_nsfw = bool(request.form.get("is_nsfw"))
    deck.is_active = bool(request.form.get("is_active"))

    db.session.commit()

    return redirect(url_for("admin_web.decks"))

@admin_web_bp.post("/decks/<string:deck_id>/delete")
@admin_required
def delete_deck(deck_id):
    deck = Deck.query.get_or_404(deck_id)
    deck.is_active = False
    db.session.commit()
    return redirect(url_for("admin_web.decks"))

@admin_web_bp.get("/questions")
@admin_required
def questions():
    deck_id = request.args.get("deck_id")
    decks = Deck.query.order_by(Deck.sort_order, Deck.name).all()

    query = Question.query
    if deck_id:
        query = query.filter_by(deck_id=deck_id)

    questions = query.order_by(Question.deck_id, Question.sort_order, Question.id).all()

    return render_template(
        "admin/questions.html",
        questions=questions,
        decks=decks,
        selected_deck_id=deck_id,
    )


@admin_web_bp.get("/questions/new")
@admin_required
def new_question():
    decks = Deck.query.filter_by(is_active=True).order_by(Deck.sort_order, Deck.name).all()
    return render_template("admin/question_form.html", question=None, decks=decks)


@admin_web_bp.post("/questions/new")
@admin_required
def create_question():
    question = Question(
        deck_id=request.form["deck_id"],
        text=request.form["text"],
        level=request.form.get("level") or "general",
        tags=[t.strip() for t in request.form.get("tags", "").split(",") if t.strip()],
        is_nsfw=bool(request.form.get("is_nsfw")),
        is_active=True,
        sort_order=int(request.form.get("sort_order") or 0),
    )

    db.session.add(question)
    db.session.commit()

    return redirect(url_for("admin_web.questions", deck_id=question.deck_id))


@admin_web_bp.get("/questions/<int:question_id>/edit")
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    decks = Deck.query.order_by(Deck.sort_order, Deck.name).all()
    return render_template("admin/question_form.html", question=question, decks=decks)


@admin_web_bp.post("/questions/<int:question_id>/edit")
@admin_required
def update_question(question_id):
    question = Question.query.get_or_404(question_id)

    question.deck_id = request.form["deck_id"]
    question.text = request.form["text"]
    question.level = request.form.get("level") or "general"
    question.tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
    question.is_nsfw = bool(request.form.get("is_nsfw"))
    question.is_active = bool(request.form.get("is_active"))
    question.sort_order = int(request.form.get("sort_order") or 0)

    db.session.commit()

    return redirect(url_for("admin_web.questions", deck_id=question.deck_id))


@admin_web_bp.post("/questions/<int:question_id>/delete")
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    deck_id = question.deck_id

    question.is_active = False
    db.session.commit()

    return redirect(url_for("admin_web.questions", deck_id=deck_id))

@admin_web_bp.get("/bulk")
@admin_required
def bulk_import():
    return render_template("admin/bulk_import.html")


@admin_web_bp.post("/bulk/decks")
@admin_required
def bulk_import_decks():
    raw = request.form.get("payload", "")

    try:
        decks = json.loads(raw)
    except json.JSONDecodeError:
        return "Invalid JSON", 400

    if not isinstance(decks, list):
        return "Payload must be a list of decks", 400

    created = 0
    updated = 0

    for item in decks:
        deck_id = item.get("id")
        if not deck_id:
            continue

        deck = Deck.query.get(deck_id)

        if deck:
            updated += 1
        else:
            deck = Deck(id=deck_id)
            db.session.add(deck)
            created += 1

        deck.name = item.get("name", deck_id)
        deck.emoji = item.get("emoji", "💬")
        deck.primary_color = item.get("primary_color", "#314755")
        deck.secondary_color = item.get("secondary_color", "#26A0DA")
        deck.description = item.get("description") or None
        deck.sort_order = int(item.get("sort_order", 0))
        deck.is_nsfw = bool(item.get("is_nsfw", False))
        deck.is_active = bool(item.get("is_active", True))

    db.session.commit()

    return redirect(url_for("admin_web.bulk_import"))


@admin_web_bp.post("/bulk/questions")
@admin_required
def bulk_import_questions():
    raw = request.form.get("payload", "")

    try:
        questions = json.loads(raw)
    except json.JSONDecodeError:
        return "Invalid JSON", 400

    if not isinstance(questions, list):
        return "Payload must be a list of questions", 400

    created = 0

    for item in questions:
        deck_id = item.get("deck_id")
        text = item.get("text")

        if not deck_id or not text:
            continue

        if not Deck.query.get(deck_id):
            continue

        existing = Question.query.filter_by(deck_id=deck_id, text=text).first()
        if existing:
            continue

        question = Question(
            deck_id=deck_id,
            text=text.strip(),
            level=item.get("level", "general"),
            tags=item.get("tags", []),
            is_nsfw=bool(item.get("is_nsfw", False)),
            is_active=bool(item.get("is_active", True)),
            sort_order=int(item.get("sort_order", 0)),
        )

        db.session.add(question)
        created += 1

    db.session.commit()

    return redirect(url_for("admin_web.bulk_import"))
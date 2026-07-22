from datetime import datetime

from flask import Blueprint, request, abort

from app.extensions import db
from app.models import PlaySession, SessionQuestion, Question, QuestionResponse

sessions_bp = Blueprint("sessions", __name__)


@sessions_bp.post("")
def create_session():
    data = request.get_json() or {}

    deck_id = data.get("deck_id")
    mode = data.get("mode", "in_person")
    user_id = data.get("user_id")
    couple_id = data.get("couple_id")
    limit = min(int(data.get("limit", 20)), 50)

    query = Question.query.filter_by(is_active=True)

    if deck_id:
        query = query.filter_by(deck_id=deck_id)

    questions = query.order_by(Question.sort_order.asc(), Question.id.asc()).limit(limit).all()

    session = PlaySession(
        user_id=user_id,
        couple_id=couple_id,
        deck_id=deck_id,
        mode=mode,
        status="active",
    )

    db.session.add(session)
    db.session.flush()

    for index, question in enumerate(questions):
        db.session.add(
            SessionQuestion(
                session_id=session.id,
                question_id=question.id,
                position=index,
            )
        )

    db.session.commit()

    return {
        "session": session_to_dict(session),
        "questions": [q.to_dict() for q in questions],
    }, 201


@sessions_bp.get("/<int:session_id>")
def get_session(session_id):
    session = PlaySession.query.get(session_id)

    if session is None:
        abort(404, description="Session not found.")

    return session_to_dict(session)


@sessions_bp.post("/<int:session_id>/finish")
def finish_session(session_id):
    session = PlaySession.query.get(session_id)

    if session is None:
        abort(404, description="Session not found.")

    session.status = "finished"
    session.finished_at = datetime.utcnow()

    db.session.commit()

    return session_to_dict(session)


@sessions_bp.post("/<int:session_id>/questions/<int:session_question_id>/skip")
def skip_session_question(session_id, session_question_id):
    session_question = SessionQuestion.query.filter_by(
        id=session_question_id,
        session_id=session_id,
    ).first()

    if session_question is None:
        abort(404, description="Session question not found.")

    session_question.was_skipped = True
    db.session.commit()

    return {
        "id": session_question.id,
        "was_skipped": session_question.was_skipped,
    }


@sessions_bp.post("/<int:session_id>/questions/<int:session_question_id>/responses")
def create_response(session_id, session_question_id):
    data = request.get_json() or {}

    session_question = SessionQuestion.query.filter_by(
        id=session_question_id,
        session_id=session_id,
    ).first()

    if session_question is None:
        abort(404, description="Session question not found.")

    response = QuestionResponse(
        session_question_id=session_question.id,
        user_id=data.get("user_id"),
        response_type=data.get("response_type", "in_person"),
        text=data.get("text"),
    )

    db.session.add(response)
    db.session.commit()

    return {
        "id": response.id,
        "session_question_id": response.session_question_id,
        "user_id": response.user_id,
        "response_type": response.response_type,
        "text": response.text,
        "created_at": response.created_at.isoformat(),
    }, 201


def session_to_dict(session):
    return {
        "id": session.id,
        "user_id": session.user_id,
        "couple_id": session.couple_id,
        "deck_id": session.deck_id,
        "mode": session.mode,
        "status": session.status,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "finished_at": session.finished_at.isoformat() if session.finished_at else None,
        "questions": [
            {
                "id": sq.id,
                "question_id": sq.question_id,
                "position": sq.position,
                "was_skipped": sq.was_skipped,
                "shown_at": sq.shown_at.isoformat() if sq.shown_at else None,
                "question": sq.question.to_dict() if sq.question else None,
            }
            for sq in session.session_questions
        ],
    }
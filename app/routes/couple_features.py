from datetime import date, datetime

from flask import Blueprint, request, abort, g
from sqlalchemy import func

from app.extensions import db
from app.auth_helpers import token_required
from app.models import (
    CoupleMember,
    Question,
    DailyCoupleQuestion,
    DailyCoupleAnswer,
    CoupleQuestionnaire,
    CoupleQuestionnaireQuestion,
    CoupleQuestionnaireSession,
    CoupleQuestionnaireAnswer,
)

couple_features_bp = Blueprint("couple_features", __name__)


def get_current_membership_or_404():
    membership = CoupleMember.query.filter_by(
        user_id=g.current_user.id
    ).first()

    if not membership:
        abort(403, description="User must belong to a couple.")

    return membership


def get_couple_members(couple_id):
    return CoupleMember.query.filter_by(couple_id=couple_id).all()


def both_members_answered_daily(daily_question):
    members = get_couple_members(daily_question.couple_id)
    member_user_ids = {m.user_id for m in members}

    answered_user_ids = {
        answer.user_id for answer in daily_question.answers
    }

    return member_user_ids.issubset(answered_user_ids) and len(member_user_ids) >= 2


def answer_to_dict(answer, include_text=False):
    return {
        "id": answer.id,
        "user_id": answer.user_id,
        "display_name": answer.user.display_name if answer.user else None,
        "answer_text": answer.answer_text if include_text else None,
        "has_answered": True,
        "created_at": answer.created_at.isoformat() if answer.created_at else None,
    }


# --------------------
# Daily Question
# --------------------

@couple_features_bp.get("/daily")
@token_required
def get_daily_question():
    membership = get_current_membership_or_404()
    today = date.today()

    daily = DailyCoupleQuestion.query.filter_by(
        couple_id=membership.couple_id,
        assigned_date=today,
    ).first()

    if not daily:
        question = (
            Question.query
            .filter_by(is_active=True, is_nsfw=False)
            .order_by(func.random())
            .first()
        )

        if not question:
            abort(404, description="No questions available.")

        daily = DailyCoupleQuestion(
            couple_id=membership.couple_id,
            question_id=question.id,
            assigned_date=today,
        )

        db.session.add(daily)
        db.session.commit()

    my_answer = DailyCoupleAnswer.query.filter_by(
        daily_question_id=daily.id,
        user_id=g.current_user.id,
    ).first()

    reveal_answers = both_members_answered_daily(daily)

    return {
        "daily_question": {
            "id": daily.id,
            "assigned_date": daily.assigned_date.isoformat(),
            "question": daily.question.to_dict() if daily.question else None,
            "my_answer": answer_to_dict(my_answer, include_text=True) if my_answer else None,
            "has_answered": my_answer is not None,
            "reveal_answers": reveal_answers,
            "answers": [
                answer_to_dict(answer, include_text=reveal_answers or answer.user_id == g.current_user.id)
                for answer in daily.answers
            ],
        }
    }


@couple_features_bp.post("/daily/answer")
@token_required
def answer_daily_question():
    membership = get_current_membership_or_404()
    data = request.get_json() or {}

    daily_question_id = data.get("daily_question_id")
    answer_text = (data.get("answer_text") or "").strip()

    if not daily_question_id:
        abort(400, description="daily_question_id is required.")

    if not answer_text:
        abort(400, description="answer_text is required.")

    daily = DailyCoupleQuestion.query.filter_by(
        id=daily_question_id,
        couple_id=membership.couple_id,
    ).first()

    if not daily:
        abort(404, description="Daily question not found.")

    answer = DailyCoupleAnswer.query.filter_by(
        daily_question_id=daily.id,
        user_id=g.current_user.id,
    ).first()

    if answer:
        answer.answer_text = answer_text
        answer.updated_at = datetime.utcnow()
    else:
        answer = DailyCoupleAnswer(
            daily_question_id=daily.id,
            user_id=g.current_user.id,
            answer_text=answer_text,
        )
        db.session.add(answer)

    db.session.commit()

    return get_daily_question()


# --------------------
# Questionnaires
# --------------------
def questionnaire_list_item(questionnaire, couple_id, user_id):
    latest_session = (
        CoupleQuestionnaireSession.query
        .filter_by(
            couple_id=couple_id,
            questionnaire_id=questionnaire.id,
        )
        .order_by(CoupleQuestionnaireSession.started_at.desc())
        .first()
    )

    payload = questionnaire.to_dict()
    payload["latest_session"] = None

    if latest_session:
        payload["latest_session"] = questionnaire_session_summary(
            session=latest_session,
            user_id=user_id,
        )

    return payload


def questionnaire_session_summary(session, user_id):
    question_ids = {
        question.id
        for question in session.questionnaire.questions
    }

    current_user_answered_ids = {
        answer.questionnaire_question_id
        for answer in session.answers
        if answer.user_id == user_id
    }

    current_user_complete = (
        bool(question_ids)
        and question_ids.issubset(current_user_answered_ids)
    )

    members = get_couple_members(session.couple_id)
    member_user_ids = {member.user_id for member in members}

    completed_user_ids = set()

    for member_user_id in member_user_ids:
        answered_ids = {
            answer.questionnaire_question_id
            for answer in session.answers
            if answer.user_id == member_user_id
        }

        if question_ids and question_ids.issubset(answered_ids):
            completed_user_ids.add(member_user_id)

    reveal_answers = (
        len(member_user_ids) >= 2
        and member_user_ids.issubset(completed_user_ids)
    )

    return {
        "id": session.id,
        "status": session.status,
        "current_user_complete": current_user_complete,
        "reveal_answers": reveal_answers,
        "started_at": (
            session.started_at.isoformat()
            if session.started_at
            else None
        ),
        "completed_at": (
            session.completed_at.isoformat()
            if session.completed_at
            else None
        ),
    }

@couple_features_bp.get("/questionnaires")
@token_required
def get_questionnaires():
    membership = get_current_membership_or_404()

    questionnaires = (
        CoupleQuestionnaire.query
        .filter_by(is_active=True)
        .order_by(
            CoupleQuestionnaire.sort_order.asc(),
            CoupleQuestionnaire.title.asc(),
        )
        .all()
    )

    return {
        "questionnaires": [
            questionnaire_list_item(
                questionnaire=questionnaire,
                couple_id=membership.couple_id,
                user_id=g.current_user.id,
            )
            for questionnaire in questionnaires
        ]
    }

@couple_features_bp.get("/questionnaires/<int:questionnaire_id>")
@token_required
def get_questionnaire(questionnaire_id):
    get_current_membership_or_404()

    questionnaire = CoupleQuestionnaire.query.filter_by(
        id=questionnaire_id,
        is_active=True,
    ).first()

    if not questionnaire:
        abort(404, description="Questionnaire not found.")

    return {
        "questionnaire": questionnaire.to_dict(),
        "questions": [q.to_dict() for q in questionnaire.questions],
    }


@couple_features_bp.post("/questionnaires/<int:questionnaire_id>/start")
@token_required
def start_questionnaire(questionnaire_id):
    membership = get_current_membership_or_404()
    data = request.get_json(silent=True) or {}

    force_new = bool(data.get("force_new", False))

    questionnaire = CoupleQuestionnaire.query.filter_by(
        id=questionnaire_id,
        is_active=True,
    ).first()

    if not questionnaire:
        abort(404, description="Questionnaire not found.")

    latest_session = (
        CoupleQuestionnaireSession.query
        .filter_by(
            couple_id=membership.couple_id,
            questionnaire_id=questionnaire.id,
        )
        .order_by(CoupleQuestionnaireSession.started_at.desc())
        .first()
    )

    if latest_session and not force_new:
        if latest_session.status != "both_complete":
            return {
                "session": latest_session.to_dict(),
                "questionnaire": questionnaire.to_dict(),
                "questions": [
                    question.to_dict()
                    for question in questionnaire.questions
                ],
                "resumed": True,
            }

        return {
            "session": latest_session.to_dict(),
            "questionnaire": questionnaire.to_dict(),
            "questions": [
                question.to_dict()
                for question in questionnaire.questions
            ],
            "results_available": True,
            "resumed": True,
        }

    if force_new and latest_session and latest_session.status != "both_complete":
        abort(
            409,
            description="Complete the current questionnaire before retaking it.",
        )

    session = CoupleQuestionnaireSession(
        couple_id=membership.couple_id,
        questionnaire_id=questionnaire.id,
        created_by_user_id=g.current_user.id,
        status="active",
    )

    db.session.add(session)
    db.session.commit()

    return {
        "session": session.to_dict(),
        "questionnaire": questionnaire.to_dict(),
        "questions": [
            question.to_dict()
            for question in questionnaire.questions
        ],
        "resumed": False,
    }, 201

@couple_features_bp.post("/questionnaires/sessions/<int:session_id>/answers")
@token_required
def submit_questionnaire_answers(session_id):
    membership = get_current_membership_or_404()
    data = request.get_json() or {}

    answers = data.get("answers", [])

    if not isinstance(answers, list):
        abort(400, description="answers must be a list.")

    session = CoupleQuestionnaireSession.query.filter_by(
        id=session_id,
        couple_id=membership.couple_id,
    ).first()

    if not session:
        abort(404, description="Questionnaire session not found.")

    valid_question_ids = {
        q.id for q in session.questionnaire.questions
    }

    for item in answers:
        questionnaire_question_id = item.get("questionnaire_question_id")
        answer_text = (item.get("answer_text") or "").strip()

        if not questionnaire_question_id or not answer_text:
            continue

        if questionnaire_question_id not in valid_question_ids:
            abort(400, description="Invalid questionnaire question.")

        existing = CoupleQuestionnaireAnswer.query.filter_by(
            session_id=session.id,
            questionnaire_question_id=questionnaire_question_id,
            user_id=g.current_user.id,
        ).first()

        if existing:
            existing.answer_text = answer_text
            existing.updated_at = datetime.utcnow()
        else:
            db.session.add(
                CoupleQuestionnaireAnswer(
                    session_id=session.id,
                    questionnaire_question_id=questionnaire_question_id,
                    user_id=g.current_user.id,
                    answer_text=answer_text,
                )
            )

    db.session.commit()
    update_questionnaire_session_status(session)

    return get_questionnaire_results_payload(session)


@couple_features_bp.get("/questionnaires/sessions/<int:session_id>/results")
@token_required
def get_questionnaire_results(session_id):
    membership = get_current_membership_or_404()

    session = CoupleQuestionnaireSession.query.filter_by(
        id=session_id,
        couple_id=membership.couple_id,
    ).first()

    if not session:
        abort(404, description="Questionnaire session not found.")

    return get_questionnaire_results_payload(session)


def update_questionnaire_session_status(session):
    members = get_couple_members(session.couple_id)
    member_user_ids = {m.user_id for m in members}

    question_ids = {q.id for q in session.questionnaire.questions}

    complete_user_ids = set()

    for user_id in member_user_ids:
        answered_ids = {
            answer.questionnaire_question_id
            for answer in session.answers
            if answer.user_id == user_id
        }

        if question_ids.issubset(answered_ids):
            complete_user_ids.add(user_id)

    if len(member_user_ids) >= 2 and member_user_ids.issubset(complete_user_ids):
        session.status = "both_complete"
        session.completed_at = datetime.utcnow()

    db.session.commit()


def get_questionnaire_results_payload(session):
    members = get_couple_members(session.couple_id)
    member_user_ids = {m.user_id for m in members}

    question_ids = {q.id for q in session.questionnaire.questions}

    current_user_answered_ids = {
        answer.questionnaire_question_id
        for answer in session.answers
        if answer.user_id == g.current_user.id
    }

    current_user_complete = question_ids.issubset(current_user_answered_ids)

    complete_user_ids = set()

    for user_id in member_user_ids:
        answered_ids = {
            answer.questionnaire_question_id
            for answer in session.answers
            if answer.user_id == user_id
        }

        if question_ids.issubset(answered_ids):
            complete_user_ids.add(user_id)

    reveal_answers = (
        len(member_user_ids) >= 2
        and member_user_ids.issubset(complete_user_ids)
    )

    return {
        "session": session.to_dict(),
        "questionnaire": session.questionnaire.to_dict(),
        "questions": [
            {
                **question.to_dict(),
                "answers": [
                    {
                        "id": answer.id,
                        "user_id": answer.user_id,
                        "display_name": answer.user.display_name if answer.user else None,
                        "answer_text": answer.answer_text if reveal_answers or answer.user_id == g.current_user.id else None,
                        "has_answered": True,
                        "created_at": answer.created_at.isoformat() if answer.created_at else None,
                    }
                    for answer in session.answers
                    if answer.questionnaire_question_id == question.id
                ],
            }
            for question in session.questionnaire.questions
        ],
        "current_user_complete": current_user_complete,
        "reveal_answers": reveal_answers,
        "completed_user_ids": list(complete_user_ids),
    }
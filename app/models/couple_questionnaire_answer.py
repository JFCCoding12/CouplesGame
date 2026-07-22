from datetime import datetime
from app.extensions import db


class CoupleQuestionnaireAnswer(db.Model):
    __tablename__ = "couple_questionnaire_answers"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer,
        db.ForeignKey("couple_questionnaire_sessions.id"),
        nullable=False,
        index=True
    )

    questionnaire_question_id = db.Column(
        db.Integer,
        db.ForeignKey("couple_questionnaire_questions.id"),
        nullable=False,
        index=True
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    answer_text = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    session = db.relationship("CoupleQuestionnaireSession", back_populates="answers")
    questionnaire_question = db.relationship("CoupleQuestionnaireQuestion")
    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint(
            "session_id",
            "questionnaire_question_id",
            "user_id",
            name="uq_questionnaire_answer_user"
        ),
    )
from datetime import datetime
from app.extensions import db


class SessionQuestion(db.Model):
    __tablename__ = "session_questions"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(db.Integer, db.ForeignKey("play_sessions.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True)

    position = db.Column(db.Integer, nullable=False)
    was_skipped = db.Column(db.Boolean, nullable=False, default=False)
    shown_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    session = db.relationship("PlaySession", back_populates="session_questions")
    question = db.relationship("Question")

    responses = db.relationship(
        "QuestionResponse",
        back_populates="session_question",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("session_id", "position", name="uq_session_question_position"),
        db.UniqueConstraint("session_id", "question_id", name="uq_session_question"),
    )
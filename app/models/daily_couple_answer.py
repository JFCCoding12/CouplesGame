from datetime import datetime
from app.extensions import db


class DailyCoupleAnswer(db.Model):
    __tablename__ = "daily_couple_answers"

    id = db.Column(db.Integer, primary_key=True)

    daily_question_id = db.Column(
        db.Integer,
        db.ForeignKey("daily_couple_questions.id"),
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

    daily_question = db.relationship("DailyCoupleQuestion", back_populates="answers")
    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint("daily_question_id", "user_id", name="uq_daily_answer_user"),
    )
from datetime import date, datetime
from app.extensions import db


class DailyCoupleQuestion(db.Model):
    __tablename__ = "daily_couple_questions"

    id = db.Column(db.Integer, primary_key=True)

    couple_id = db.Column(db.Integer, db.ForeignKey("couples.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True)

    assigned_date = db.Column(db.Date, nullable=False, default=date.today, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    couple = db.relationship("Couple")
    question = db.relationship("Question")

    answers = db.relationship(
        "DailyCoupleAnswer",
        back_populates="daily_question",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("couple_id", "assigned_date", name="uq_couple_daily_question"),
    )
from datetime import datetime
from app.extensions import db


class FavoriteQuestion(db.Model):
    __tablename__ = "favorite_questions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship("User", back_populates="favorites")
    question = db.relationship("Question")

    __table_args__ = (
        db.UniqueConstraint("user_id", "question_id", name="uq_user_favorite_question"),
    )
from datetime import datetime
from app.extensions import db


class QuestionResponse(db.Model):
    __tablename__ = "question_responses"

    id = db.Column(db.Integer, primary_key=True)

    session_question_id = db.Column(
        db.Integer,
        db.ForeignKey("session_questions.id"),
        nullable=False,
        index=True
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)

    response_type = db.Column(db.String(40), nullable=False, default="in_person")
    text = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    session_question = db.relationship("SessionQuestion", back_populates="responses")
    user = db.relationship("User", back_populates="responses")
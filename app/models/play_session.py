from datetime import datetime
from app.extensions import db


class PlaySession(db.Model):
    __tablename__ = "play_sessions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    couple_id = db.Column(db.Integer, db.ForeignKey("couples.id"), nullable=True, index=True)

    deck_id = db.Column(db.String(80), db.ForeignKey("decks.id"), nullable=True, index=True)

    mode = db.Column(db.String(40), nullable=False, default="in_person")
    status = db.Column(db.String(40), nullable=False, default="active")

    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="sessions")
    couple = db.relationship("Couple", back_populates="sessions")
    deck = db.relationship("Deck")

    session_questions = db.relationship(
        "SessionQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionQuestion.position",
    )
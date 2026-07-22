from datetime import datetime
from app.extensions import db


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)

    deck_id = db.Column(
        db.String(80),
        db.ForeignKey("decks.id"),
        nullable=False,
        index=True
    )

    text = db.Column(db.Text, nullable=False)

    level = db.Column(db.String(40), nullable=False, default="general")
    tags = db.Column(db.JSON, nullable=False, default=list)

    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    is_nsfw = db.Column(db.Boolean, nullable=False, default=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    deck = db.relationship("Deck", back_populates="questions")

    def to_dict(self):
        return {
            "id": self.id,
            "deck_id": self.deck_id,
            "text": self.text,
            "level": self.level,
            "tags": self.tags or [],
            "is_nsfw": self.is_nsfw,
            "sort_order": self.sort_order
        }
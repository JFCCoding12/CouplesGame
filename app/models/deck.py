from datetime import datetime
from app.extensions import db


class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.String(80), primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    emoji = db.Column(db.String(20), nullable=False)
    primary_color = db.Column(db.String(20), nullable=False, default="#EC4899")
    secondary_color = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)

    is_nsfw = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    questions = db.relationship(
        "Question",
        back_populates="deck",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def to_dict(self):
        active_questions = [q for q in self.questions if q.is_active]

        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "description": self.description,
            "question_count": len(active_questions),
            "is_nsfw": self.is_nsfw,
            "sort_order": self.sort_order,
        }
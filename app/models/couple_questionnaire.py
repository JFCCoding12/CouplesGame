from datetime import datetime
from app.extensions import db


class CoupleQuestionnaire(db.Model):
    __tablename__ = "couple_questionnaires"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(160), nullable=False)
    subtitle = db.Column(db.String(255), nullable=True)

    emoji = db.Column(db.String(20), nullable=False, default="📝")

    primary_color = db.Column(db.String(20), nullable=False, default="#C33764")
    secondary_color = db.Column(db.String(20), nullable=False, default="#FF6B6B")

    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_nsfw = db.Column(db.Boolean, nullable=False, default=False)

    sort_order = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    questions = db.relationship(
        "CoupleQuestionnaireQuestion",
        back_populates="questionnaire",
        cascade="all, delete-orphan",
        order_by="CoupleQuestionnaireQuestion.position"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "emoji": self.emoji,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "is_active": self.is_active,
            "is_nsfw": self.is_nsfw,
            "sort_order": self.sort_order,
            "question_count": len(self.questions),
        }
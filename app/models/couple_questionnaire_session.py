from datetime import datetime
from app.extensions import db


class CoupleQuestionnaireSession(db.Model):
    __tablename__ = "couple_questionnaire_sessions"

    id = db.Column(db.Integer, primary_key=True)

    couple_id = db.Column(db.Integer, db.ForeignKey("couples.id"), nullable=False, index=True)
    questionnaire_id = db.Column(
        db.Integer,
        db.ForeignKey("couple_questionnaires.id"),
        nullable=False,
        index=True
    )

    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    status = db.Column(db.String(40), nullable=False, default="active")
    # active, both_complete, archived

    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    couple = db.relationship("Couple")
    questionnaire = db.relationship("CoupleQuestionnaire")
    created_by = db.relationship("User")

    answers = db.relationship(
        "CoupleQuestionnaireAnswer",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "couple_id": self.couple_id,
            "questionnaire_id": self.questionnaire_id,
            "created_by_user_id": self.created_by_user_id,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
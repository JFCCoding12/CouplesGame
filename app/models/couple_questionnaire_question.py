from datetime import datetime
from app.extensions import db


class CoupleQuestionnaireQuestion(db.Model):
    __tablename__ = "couple_questionnaire_questions"

    id = db.Column(db.Integer, primary_key=True)

    questionnaire_id = db.Column(
        db.Integer,
        db.ForeignKey("couple_questionnaires.id"),
        nullable=False,
        index=True
    )

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=True, index=True)

    text = db.Column(db.Text, nullable=False)

    position = db.Column(db.Integer, nullable=False, default=0)
    is_required = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    questionnaire = db.relationship("CoupleQuestionnaire", back_populates="questions")
    source_question = db.relationship("Question")

    def to_dict(self):
        return {
            "id": self.id,
            "questionnaire_id": self.questionnaire_id,
            "question_id": self.question_id,
            "text": self.text,
            "position": self.position,
            "is_required": self.is_required,
        }
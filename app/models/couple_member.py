from datetime import datetime
from app.extensions import db


class CoupleMember(db.Model):
    __tablename__ = "couple_members"

    id = db.Column(db.Integer, primary_key=True)

    couple_id = db.Column(db.Integer, db.ForeignKey("couples.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    role = db.Column(db.String(40), nullable=False, default="member")

    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    couple = db.relationship("Couple", back_populates="members")
    user = db.relationship("User")

    __table_args__ = (
        db.UniqueConstraint("couple_id", "user_id", name="uq_couple_member"),
    )
from datetime import datetime
from app.extensions import db


class Couple(db.Model):
    __tablename__ = "couples"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(160), nullable=True)
    invite_code = db.Column(db.String(40), unique=True, nullable=False, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    members = db.relationship("CoupleMember", back_populates="couple", cascade="all, delete-orphan")
    sessions = db.relationship("PlaySession", back_populates="couple")
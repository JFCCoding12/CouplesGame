from app.extensions import db
from app.models import Deck, Question


def seed_data():
    d = Deck(
        id="deep",
        name="Deep Conversations",
        emoji="🌙",
        primary_color="#314755",
        secondary_color="#26A0DA",
        description="Cool Description",
        sort_order=0,
    )

    if not Deck.query.get(d.id):
        db.session.add(d)

    if not Question.query.first():
        db.session.add(
            Question(
                deck_id="deep",
                text="What is something you wish people understood about you?"
            )
        )

    db.session.commit()
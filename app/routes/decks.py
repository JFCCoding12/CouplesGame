from flask import Blueprint
from app.models import Deck
decks_bp=Blueprint("decks",__name__)
@decks_bp.get("")
def decks(): return {"decks":[d.to_dict() for d in Deck.query.filter_by(is_active=True).order_by(Deck.sort_order).all()]}

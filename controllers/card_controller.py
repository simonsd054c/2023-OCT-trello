from datetime import date
import functools

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, cards_schema, card_schema
from models.user import User
from controllers.comment_controller import comments_bp

cards_bp = Blueprint('cards', __name__, url_prefix='/cards')
cards_bp.register_blueprint(comments_bp)

def authorise_as_admin(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        stmt = db.select(User).filter_by(id=user_id)
        user = db.session.scalar(stmt)
        # if the user is an admin
        if user.is_admin:
            # we will continue and run the decorated function
            return fn(*args, **kwargs)
        # else (if the user is NOT an admin)
        else:
            # return an error
            return {"error": "Not authorised to delete a card"}, 403
        
    return wrapper

# http://localhost:8080/cards - GET
@cards_bp.route('/')
def get_all_cards():
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return cards_schema.dump(cards)


# http://localhost:8080/cards/4 - GET
@cards_bp.route('/<int:card_id>')
def get_one_card(card_id): # card_id = 4
    stmt = db.select(Card).filter_by(id=card_id) # select * from cards where id=4
    card = db.session.scalar(stmt)
    if card:
        return card_schema.dump(card)
    else:
        return {"error": f"Card with id {card_id} not found"}, 404
    

# http://localhost:8080/cards - POST
@cards_bp.route('/', methods=["POST"])
@jwt_required()
def create_card():
    body_data = card_schema.load(request.get_json())
    # Create a new card model instance
    card = Card(
        title = body_data.get('title'),
        description = body_data.get('description'),
        date = date.today(),
        status = body_data.get('status'),
        priority = body_data.get('priority'),
        user_id = get_jwt_identity()
    )
    # Add that to the session and commit
    db.session.add(card)
    db.session.commit()
    # return the newly created card
    return card_schema.dump(card), 201

# https://localhost:8080/cards/6 - DELETE
@cards_bp.route('/<int:card_id>', methods=["DELETE"])
@jwt_required()
@authorise_as_admin
def delete_card(card_id):
    # # check user's admin status
    # is_admin = is_user_admin()
    # if not is_admin:
    #     return {"error": "Not authorised to delete a card"}, 403
    # get the card from the db with id = card_id
    stmt = db.select(Card).where(Card.id == card_id)
    card = db.session.scalar(stmt)
    # if card exists
    if card:
        # delete the card from the session and commit
        db.session.delete(card)
        db.session.commit()
        # return msg
        return {'message': f"Card '{card.title}' deleted successfully"}
    # else
    else:
        # return error msg
        return {'error': f"Card with id {card_id} not found"}, 404
    
# http://localhost:8080/cards/5 - PUT, PATCH
@cards_bp.route('/<int:card_id>', methods=["PUT", "PATCH"])
@jwt_required()
def update_card(card_id):
    # Get the data to be updated from the body of the request
    body_data = card_schema.load(request.get_json(), partial=True)
    # get the card from the db whose fields need to be updated
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    # if card exists
    if card:
        if str(card.user_id) != get_jwt_identity():
            return {"error": "Only the owner can edit the card"}, 403
        # update the fields
        card.title = body_data.get('title') or card.title
        card.description = body_data.get('description') or card.description
        card.status = body_data.get('status') or card.status
        card.priority = body_data.get('priority') or card.priority
        # commit the changes
        db.session.commit()
        # return the updated card back
        return card_schema.dump(card)
    # else
    else:
        # return error msg
        return {'error': f'Card with id {card_id} not found'}, 404
    

# This function has been replaced by the authorise_as_admin decorator
def is_user_admin():
    user_id = get_jwt_identity()
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.scalar(stmt)
    return user.is_admin

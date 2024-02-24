from marshmallow import fields, validates
from marshmallow.validate import Length, And, Regexp, OneOf
from marshmallow.exceptions import ValidationError

from init import db, ma

VALID_STATUSES = ('To Do', 'Ongoing', 'Done', 'Testing', 'Deployed')
VALID_PRIORITIES = ('Low', 'Medium', 'High', 'Urgent')

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    date = db.Column(db.Date) # Date the card was created
    status = db.Column(db.String)
    priority = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='cards')
    comments = db.relationship('Comment', back_populates='card', cascade='all, delete')

    # {id: 1, title: Card 1, user_id: 2}
    # {
    #   id: 1,
    #   title: Card 1,
    #   user: {
    #       name: User 1,
    #       email: user1@email.com
    #   }
    # }

class CardSchema(ma.Schema):

    title = fields.String(required=True, validate=And(
        Length(min=2, error="Title must be at least 2 characters long"),
        Regexp('^[a-zA-Z0-9 ]+$', error="Title can only have alphanumeric characters")
    ))

    status = fields.String(validate=OneOf(VALID_STATUSES))

    priority = fields.String(validate=OneOf(VALID_PRIORITIES))

    # There can only be one card with status 'Ongoing'
    @validates('status')
    def validate_status(self, value):
        if value == VALID_STATUSES[1]:
            stmt = db.select(db.func.count()).select_from(Card).filter_by(status=VALID_STATUSES[1])
            count = db.session.scalar(stmt)
            if count > 0:
                raise ValidationError('You already have an ongoing card')

    user = fields.Nested('UserSchema', only = ['name', 'email'])

    comments = fields.List(fields.Nested('CommentSchema', exclude=['card']))

    class Meta:
        fields = ('id', 'title', 'description', 'date', 'status', 'priority', 'user', 'comments')
        ordered = True

card_schema = CardSchema()
cards_schema = CardSchema(many=True)
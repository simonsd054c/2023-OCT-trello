from init import db, ma
from marshmallow import fields

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey("cards.id"), nullable=False)

    # fetch comment with id 1
    # {id: 1, message: 'Comment 1', user_id: 1, card_id: 2}

    user = db.relationship('User', back_populates='comments')
    card = db.relationship('Card', back_populates='comments')

    # fetch comment with id 1
    '''
    {
      id: 1,
      message: 'Comment 1',
      user: {
        name: 'User 1',
        email: 'user1@email.com'
      },
      card: {
        id: 2,
        title: 'Card 2',
        description: 'Card 2 desc'
        ...
        ...
        ...
      }
    }
    '''


# comment schema
class CommentSchema(ma.Schema):
    
    user = fields.Nested('UserSchema', only=['name', 'email'])

    card = fields.Nested('CardSchema', exclude=['comments'])

    class Meta:
        fields = ('id', 'message', 'user', 'card')


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
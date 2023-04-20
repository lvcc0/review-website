import sqlalchemy as sa
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Association(SqlAlchemyBase):
    __tablename__ = 'users_to_reviews'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    review_id = sa.Column(sa.Integer, sa.ForeignKey('reviews.id'))

    users = orm.relationship('User', backref='users')
    reviews = orm.relationship('Review', backref='reviews')

import sqlalchemy as sa
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


review_to_relation = sa.Table(
    'review_association',
    SqlAlchemyBase.metadata,
    sa.Column('reviews', sa.Integer, sa.ForeignKey('reviews.id')),
    sa.Column('user_relations', sa.Integer, sa.ForeignKey('user_relations.id'))
)

user_to_relation = sa.Table(
    'user_association',
    SqlAlchemyBase.metadata,
    sa.Column('users', sa.Integer, sa.ForeignKey('users.id')),
    sa.Column('user_relations', sa.Integer, sa.ForeignKey('user_relations.id'))
)


class UserGame(SqlAlchemyBase):
    __tablename__ = 'user_relations'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    steam_id = sa.Column(sa.Integer, nullable=False)
    review_id = sa.Column(sa.Integer, sa.ForeignKey('reviews.id'))

    user = orm.relationship('User')
    review = orm.relationship('Review')

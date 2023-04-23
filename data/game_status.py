import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Status(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'game_status'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    steam_id = sa.Column(sa.Integer)
    status = sa.Column(sa.Integer)

    users = orm.relationship('User')

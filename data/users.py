import sqlalchemy as sa
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    nickname = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True)

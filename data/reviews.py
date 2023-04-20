import sqlalchemy as sa
from sqlalchemy import orm
from datetime import datetime

from .db_session import SqlAlchemyBase


class Review(SqlAlchemyBase):
    __tablename__ = 'reviews'

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    content = sa.Column(sa.String)
    positive = sa.Column(sa.Boolean, default=True)
    is_private = sa.Column(sa.Boolean, default=True)
    created_date = sa.Column(sa.DateTime, default = datetime.now)
    steam_id = sa.Column(sa.Integer)

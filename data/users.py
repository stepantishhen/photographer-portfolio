import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    heading = sqlalchemy.Column(sqlalchemy.String, default='Без имени')
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
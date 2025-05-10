import sqlalchemy
from .db_session import SqlAlchemyBase


class Kategory(SqlAlchemyBase):
    __tablename__ = 'kategory'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    kategor = sqlalchemy.Column(sqlalchemy.String, nullable = False)

    def __repr__(self):
        return f'{self.id}'



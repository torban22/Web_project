import sqlalchemy
from .db_session import SqlAlchemyBase


class Country(SqlAlchemyBase):
    __tablename__ = 'country'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable = False)

    def __repr__(self):
        return f'{self.id}'
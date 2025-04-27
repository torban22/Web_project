import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship

from .db_session import SqlAlchemyBase


class Country(SqlAlchemyBase):
    __tablename__ = 'country'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable = False)

    #cat = relationship('Catalog', backref ='countr')
    #country = orm.relationship("Country", back_populates='catalog')
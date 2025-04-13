import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase



class Kategory(SqlAlchemyBase):
    __tablename__ = 'kategory'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    kategor = sqlalchemy.Column(sqlalchemy.String, nullable = False)
    '''catalog = orm.relationship('Catalog')
    kate = orm.relationship("Kategory", back_populates='catalog')
    reserve = orm.relationship('Reserve')
    kateg = orm.relationship("Kategory", back_populates='reserve')'''



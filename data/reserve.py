import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from .db_session import SqlAlchemyBase


class Reserve(SqlAlchemyBase):
    __tablename__ = 'reserve'
    id_res = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_tov = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('catalog.id'))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    kategory_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('kategory.id'))
    lon = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    lat = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    tov_num = relationship('Catalog', backref ='ct')
    ktgr = relationship('Kategory', backref ='ct')

    def __repr__(self):
        return f'{self.id_res} {self.id_tov} {self.quantity} {self.price} {self.tov_num.name}'



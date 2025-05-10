from sqlalchemy.orm import relationship
import sqlalchemy
from .db_session import SqlAlchemyBase


class Catalog(SqlAlchemyBase):
    __tablename__ = 'catalog'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable = False)
    kategory_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('kategory.id'))
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    country_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('country.id'))
    haracteristic = sqlalchemy.Column(sqlalchemy.String, nullable = False)
    image = sqlalchemy.Column(sqlalchemy.String, nullable = False)
    '''reserve = orm.relationship('Reserve')
    katal = orm.relationship("Catalog", back_populates='reserve')'''
    countr = relationship('Country', backref ='cat')
    kateg = relationship('Kategory', backref ='cat')

    def __repr__(self):
        return f'{self.id} {self.name} {self.quantity} {self.price} {self.kategory_id} {self.image}'



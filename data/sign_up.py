import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Sign_up(SqlAlchemyBase, UserMixin):
    __tablename__ = 'sign_up'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable = True)

    email = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, passwor):
        self.password = generate_password_hash(passwor)

    def check_password(self, passwor):
        return check_password_hash(self.password, passwor)

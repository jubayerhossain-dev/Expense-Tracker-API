from Database_connection import Base
from sqlalchemy import Column, String, Integer, Boolean, Float, Date, ForeignKey


class TransactionTable(Base):
    __tablename__ = 'transaction'

    id = Column(Integer, primary_key=True, index= True)
    title = Column(String)
    amount = Column(Float)
    type = Column(String)
    category = Column(String)
    date = Column(Date)
    owner_id = Column(Integer, ForeignKey('user.id'))

class UserTable(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQL_DATABASE_URL = 'postgresql://postgres:12345@localhost/Transaction'

engine = create_engine(SQL_DATABASE_URL)
sessionlocal = sessionmaker(autoflush= False, autocommit= False, bind=engine)
Base = declarative_base()
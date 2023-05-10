from enum import unique
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Column,String,Integer,Float,ForeignKey,DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# we will create out users table

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(50), unique=True)
    name = Column(String(50))
    password = Column(String(64))
    group = Column(Integer, default=1)
    created_at = Column(DateTime,default=datetime.utcnow, nullable=False )

    def __repr__(self) -> str:
        return f"{self.id}|{self.name}|{self.group}"

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    path = Column(String(255))
    added_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime,default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"{self.id}|{self.path}|{self.added_by}"

def open_database():
    engine = create_engine('sqlite:///database.sqlite')
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    engine = create_engine('sqlite:///database.sqlite')
    Base.metadata.create_all(engine)
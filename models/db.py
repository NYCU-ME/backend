from sqlalchemy import Column, String,\
    Integer, DateTime, ForeignKey, Text, CHAR, BOOLEAN
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String(16), primary_key=True)
    name = Column(String(256), nullable=False)
    username = Column(String(256), nullable=False)
    password = Column(String(100), nullable=False, default='')
    status = Column(String(16), nullable=False)
    email = Column(String(256), nullable=False)
    limit = Column(Integer, nullable=False, default=2)
    isAdmin = Column(Integer, nullable=False, default=0)

    # Relationships
    domains = relationship("Domain", backref="user")

class Domain(Base):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String(16), ForeignKey('users.id'), nullable=False)
    domain = Column(Text)
    regDate = Column(DateTime)
    expDate = Column(DateTime)
    status = Column(BOOLEAN, default=True)

    # Relationships
    records = relationship("Record", backref="domain")

class Record(Base):
    __tablename__ = 'records'

    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    type = Column(CHAR(16), nullable=False)
    value = Column(String(256))
    ttl = Column(Integer, nullable=False)
    regDate = Column(DateTime)
    expDate = Column(DateTime)
    status = Column(BOOLEAN, default=True)

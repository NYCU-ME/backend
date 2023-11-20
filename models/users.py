from sqlalchemy.orm import sessionmaker
from . import db
import logging
class Users:
    def __init__(self, sql_engine):
        Session = sessionmaker(bind=sql_engine)
        self.session = Session()
    
    def query(self, uid):
        user = self.session.query(db.User).filter_by(id=uid).all()
        if len(user):
            return user[0]
        return None

    def add(self, uid, name, username, password, status, email):
        user = db.User(id=uid, 
                       name=name, 
                       username=username, 
                       password=password, 
                       status=status, 
                       email=email)
        self.session.add(user)
        self.session.commit()

    def update_email(self, uid, email):
        user = self.query(uid)
        user.email = email
        self.session.commit()

    def __del__(self):
        self.session.close()

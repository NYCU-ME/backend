from sqlalchemy.orm import sessionmaker, scoped_session
from . import db
import logging

class Users:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine
        self.Session = scoped_session(sessionmaker(bind=self.sql_engine))

    def query(self, uid):
        session = self.Session()
        try:
            user = session.query(db.User).filter_by(id=uid).first()
            return user
        except Exception as e:
            logging.error(f"Error querying user: {e}")
            return None
        finally:
            session.close() 

    def add(self, uid, name, username, password, status, email):
        session = self.Session()
        try:
            user = db.User(id=uid, name=name, username=username, password=password, status=status, email=email)
            session.add(user)
            session.commit()
        except Exception as e:
            logging.error(f"Error adding user: {e}")
            session.rollback()
        finally:
            session.close()

    def update_email(self, uid, email):
        session = self.Session()
        try:
            user = session.query(db.User).filter_by(id=uid).first()
            if user:
                user.email = email
                session.commit()
        except Exception as e:
            logging.error(f"Error updating user email: {e}")
            session.rollback()
        finally:
            session.close()


import logging
from sqlalchemy.orm import sessionmaker, scoped_session
from . import db

class Users:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine
        self.session_factory = scoped_session(sessionmaker(bind=self.sql_engine))

    def query(self, uid):
        session = self.session_factory()
        try:
            user = session.query(db.User).filter_by(id=uid).first()
            return user
        except Exception as e:
            logging.error("Error querying user: %s", e)
            return None
        finally:
            session.close()

    def add(self, uid, name, username, password, status, email):
        session = self.session_factory()
        try:
            user = db.User(id=uid, name=name, username=username, password=password,
                           status=status, email=email)
            session.add(user)
            session.commit()
        except Exception as e:
            logging.error("Error adding user: %s", e)
            session.rollback()
        finally:
            session.close()

    def update_email(self, uid, email):
        session = self.session_factory()
        try:
            user = session.query(db.User).filter_by(id=uid).first()
            if user:
                user.email = email
                session.commit()
        except Exception as e:
            logging.error("Error updating user email: %s", e)
            session.rollback()
        finally:
            session.close()

    def update_password(self, uid, password):
        session = self.session_factory()
        try:
            user = session.query(db.User).filter_by(id=uid).first()
            if user:
                user.password = password
                session.commit()
        except Exception as e:
            logging.error("Error updating user password: %s", e)
            session.rollback()
        finally:
            session.close()

    def count_user(self):
        session = self.session_factory()
        try:
            count = session.query(db.User).count()
            return count
        except Exception as e:
            logging.error("Error counting user: %s", e)
            return 0
        finally:
            session.close()

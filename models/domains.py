from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime, timedelta
from . import db
import logging

class Domains:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine
        self.make_session = scoped_session(sessionmaker(bind=self.sql_engine))

    def get_domain(self, domain_name):
        session = self.make_session()
        try:
            domain = session.query(db.Domain).filter_by(domain=domain_name, status=1).first()
            return domain
        finally:
            session.close()

    def get_expired_domain(self):
        session = self.make_session()
        try:
            now = datetime.now()
            domain = session.query(db.Domain).filter_by(status=1).filter(db.Domain.expDate < now).first()
            return domain
        finally:
            session.close()

    def get_domain_by_id(self, domain_id):
        session = self.make_session()
        try:
            domain = session.query(db.Domain).filter_by(id=domain_id, status=1).first()
            return domain
        finally:
            session.close()

    def list_by_user(self, user_id):
        session = self.make_session()
        try:
            domains = session.query(db.Domain).filter_by(userId=user_id, status=1).all()
            return domains
        finally:
            session.close()

    def register(self, domain_name, user_id):
        session = self.make_session()
        try:
            now = datetime.now()
            domain = db.Domain(userId=user_id,
                               domain=domain_name,
                               regDate=now,
                               expDate=now + timedelta(days=30),
                               status=1)
            session.add(domain)
            session.commit()
        except Exception as e:
            logging.error(f"Error registering domain: {e}")
            session.rollback()
        finally:
            session.close()

    def renew(self, domain_name):
        session = self.make_session()
        try:
            domain = session.query(db.Domain).filter_by(domain=domain_name, status=1).first()
            if domain:
                domain.expDate = datetime.now() + timedelta(days=30)
                session.commit()
        except Exception as e:
            logging.error(f"Error renewing domain: {e}")
            session.rollback()
        finally:
            session.close()

    def release(self, domain_name):
        session = self.make_session()
        try:
            domain = session.query(db.Domain).filter_by(domain=domain_name, status=1).first()
            if domain:
                domain.expDate = datetime.now()
                domain.status = 0
                session.commit()
        except Exception as e:
            logging.error(f"Error releasing domain: {e}")
            session.rollback()
        finally:
            session.close()


from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session

from . import db

class Glues:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine
        self.session_factory = scoped_session(sessionmaker(bind=self.sql_engine))

    def get_record(self, glue_id):
        session = self.session_factory()
        try:
            return session.query(db.Glue).filter_by(id=glue_id, status=1).first()
        finally:
            session.close()

    def get_records(self, domain_id):
        session = self.session_factory()
        try:
            return session.query(db.Glue).filter_by(domain=domain_id, status=1).all()
        finally:
            session.close()

    def get_record_by_type_value(self, domain_id, subdomain, type_, value):
        session = self.session_factory()
        try:
            return session.query(db.Glue).filter_by(domain=domain_id,
                                                      subdomain=subdomain,
                                                      type=type_,
                                                      value=value,
                                                      status=1).first()
        finally:
            session.close()

    def add_record(self, domain_id, subdomain, type_, value, ttl):
        session = self.session_factory()
        try:
            new_record = db.Glue(
                    domain=domain_id,
                    subdomain=subdomain,
                    type=type_, value=value,
                    ttl=ttl,
                    status=1,
                    regDate=datetime.now()
            )
            session.add(new_record)
            session.commit()
            return new_record
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def del_record(self, glue_id):
        session = self.session_factory()
        try:
            record_to_delete = session.query(db.Glue).filter_by(id=glue_id).first()
            if record_to_delete:
                record_to_delete.expDate = datetime.now()
                record_to_delete.status = 0
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

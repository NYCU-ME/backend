from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session

from . import db

class Records:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine
        self.session_factory = scoped_session(sessionmaker(bind=self.sql_engine))

    def get_record(self, record_id):
        session = self.session_factory()
        try:
            return session.query(db.Record).filter_by(id=record_id, status=1).first()
        finally:
            session.close()

    def get_records(self, domain_id):
        session = self.session_factory()
        try:
            return session.query(db.Record).filter_by(domain=domain_id, status=1).all()
        finally:
            session.close()

    def get_record_by_type_value(self, domain_id, type_, value):
        session = self.session_factory()
        try:
            return session.query(db.Record).filter_by(domain=domain_id,
                                                      type=type_,
                                                      value=value,
                                                      status=1).first()
        finally:
            session.close()

    def add_record(self, domain_id, record_type, value, ttl):
        session = self.session_factory()
        try:
            record = db.Record(domain=domain_id,
                               type=record_type,
                               value=value,
                               ttl=ttl,
                               regDate=datetime.now(),
                               status=1)
            session.add(record)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def del_record_by_id(self, record_id):
        session = self.session_factory()
        try:
            record = session.query(db.Record).filter_by(id=record_id).first()
            if record:
                record.status = 0
                record.expDate = datetime.now()
                session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

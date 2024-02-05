from datetime import datetime
from sqlalchemy.orm import sessionmaker, scoped_session

from . import db
class Dnskeys:
    def __init__(self, sql_engine):
        self.sql_engine = sql_engine
        self.session_factory = scoped_session(sessionmaker(bind=self.sql_engine))

    def add_dnskey_record(self, domain_id, flag, algorithm, value, ttl):
        session = self.session_factory()
        try:
            new_dnskey = db.Dnskey(
                domain=domain_id,
		flag=flag,
                algorithm=algorithm,
                value=value,
                ttl=ttl,
                regDate=datetime.now(),
                status=1
            )
            session.add(new_dnskey)
            session.commit()
            return new_dnskey
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def del_dnskey_record(self, dnskey_id):
        session = self.session_factory()
        try:
            dnskey_to_remove = session.query(db.Dnskey).filter_by(id=dnskey_id).first()
            if dnskey_to_remove:
                dnskey_to_remove.expDate = datetime.now()
                dnskey_to_remove.status = 0
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_records(self, domain_id):
        session = self.session_factory()
        try:
            return session.query(db.Dnskey).filter_by(domain=domain_id, status=1).all()
        finally:
            session.close()

    def get_dnskey_by_value(self, domain_id, flag, algorithm, value):
        session = self.session_factory()
        try:
            return session.query(db.Dnskey).filter_by(
                domain=domain_id,
		flag=flag,
                algorithm=algorithm,
                value=value,
                status=1
            ).first()
        finally:
            session.close()

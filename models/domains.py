from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from . import db


class Domains:
    def __init__(self, sql_engine):
        Session = sessionmaker(bind=sql_engine)
        self.session = Session()

    def get_domain(self, domain):
        domain = self.session.query(db.Domain).filter_by(domain=domain, status=1).all()
        if domain:
            return domain[0]
        return None

    def get_domain_by_id(self, domain_id):
        domain = self.session.query(db.Domain).filter_by(id=domain_id, status=1).all()
        if domain:
            return domain[0]
        return None

    def list_by_user(self, user):
        domains = self.session.query(db.Domain).filter_by(userId=user, status=1).all()
        return domains

    def register(self, domain, user):
        now = datetime.now()
        regDate = now
        expDate = (now + timedelta(days=30))
        domain = db.Domain(userId = user,
                           domain = domain,
                           regDate = regDate,
                           expDate = expDate,
                           status = 1)
        self.session.add(domain)
        self.session.commit()

    def renew(self, domain):
        domain = self.get_domain(domain)
        if domain != None:
            now = datetime.now()
            expDate = (now + timedelta(days=30))
            domain.expDate = expDate
            self.session.commit()

    def release(self, domain):
        domain = self.get_domain(domain)
        if domain != None:
            expDate = datetime.now() 
            domain.expDate = expDate
            domain.status = 0
            self.session.commit()

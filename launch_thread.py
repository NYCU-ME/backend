import logging
import os
import time
from sqlalchemy import create_engine

import config
from models import Users, Domains, Records, DDNS, db
from services import AuthService, DNSService

def recycle():
    while (domain := dnsService.get_expired_domain()) != None:
        logging.info(f"recycling {domain.domain}")
        dnsService.release_domain(domain.domain)

env_test = os.getenv('TEST')

sql_engine = None
if env_test is not None:
    sql_engine = create_engine("sqlite:///:memory:")
    db.Base.metadata.create_all(sql_engine)
else:
    sql_engine = create_engine(
        'mysql+pymysql://{user}:{pswd}@{host}/{db}'.format(
            user=config.MYSQL_USER,
            pswd=config.MYSQL_PSWD,
            host=config.MYSQL_HOST,
            db=config.MYSQL_DB
        )
    )

ddns = DDNS(logging, config.DDNS_KEY, config.DDNS_SERVER, config.DDNS_ZONE)

users = Users(sql_engine)
domains = Domains(sql_engine)
records = Records(sql_engine)

authService = AuthService(logging, config.JWT_SECRET, users, domains)
dnsService = DNSService(logging, users, domains, records, ddns, config.HOST_DOMAINS)

if __name__ == "__main__":
    while True:
        recycle()
        time.sleep(1)

import logging
import os
import time
from sqlalchemy import create_engine

import config
from models import Users, Domains, Records, Glues, Dnskeys, DDNS, db
from services import AuthService, DNSService

def recycle(local_dns_service):
    try:
        while (domain := local_dns_service.get_expired_domain()) is not None:
            logging.info("recycling %s", domain.domain)
            local_dns_service.release_domain(domain.domain)
    except Exception:
        pass

ENV_TEST = os.getenv('TEST')

SQL_ENGINE = None
if ENV_TEST is not None:
    SQL_ENGINE = create_engine("sqlite:///:memory:")
    db.Base.metadata.create_all(SQL_ENGINE)
else:
    connection_string = (
        f"mysql+pymysql://{config.MYSQL_USER}:{config.MYSQL_PSWD}"
        f"@{config.MYSQL_HOST}/{config.MYSQL_DB}"
    )
    SQL_ENGINE = create_engine(connection_string)

ddns = DDNS(logging, config.DDNS_KEY, config.DDNS_SERVER, config.DDNS_ZONE)

users = Users(SQL_ENGINE)
domains = Domains(SQL_ENGINE)
records = Records(SQL_ENGINE)
glues = Glues(SQL_ENGINE)
dnskeys = Dnskeys(SQL_ENGINE)

auth_service = AuthService(logging, config.JWT_SECRET, users, domains)
dns_service = DNSService(logging,
                         users,
                         domains,
                         records,
                         glues,
                         dnskeys,
                         ddns,
                         config.HOST_DOMAINS)

if __name__ == "__main__":
    while True:
        recycle(dns_service)
        time.sleep(1)

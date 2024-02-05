import logging
import time
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Domains, Records, Users, Glues, Dnskeys, db, DDNS
from services import DNSService
import config
from launch_thread import recycle

ddns = DDNS(logging, "/etc/ddnskey.conf", "172.21.21.3", "nycu-dev.me")

sql_engine = create_engine("sqlite:///:memory:")
db.Base.metadata.create_all(sql_engine)
Session = sessionmaker(bind=sql_engine)
session = Session()

users = Users(sql_engine)
domains = Domains(sql_engine)
records = Records(sql_engine)
glues = Glues(sql_engine)
dnskeys = Dnskeys(sql_engine)

dnsService = DNSService(logging, users, domains, records, glues, dnskeys, ddns, config.HOST_DOMAINS)

def test_domain_expire():
    exp_date = datetime.now() + timedelta(seconds=5)
    domain = db.Domain(userId="109550028",
                       domain="test-expire.nycu-dev.me",
                       regDate=datetime.now(),
                       expDate=exp_date,
                       status=1)
    session.add(domain)
    session.commit()

    time.sleep(10)
    recycle(dnsService)
    assert dnsService.get_domain("test-expire.nycu-dev.me") is None

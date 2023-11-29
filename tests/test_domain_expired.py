from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from datetime import timedelta
import time
import logging

from models import Domains, Records, Users, db, DDNS
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

dnsService = DNSService(logging, users, domains, records, ddns, config.HOST_DOMAINS)

def test_domain_expire():
    # Insert an expiring domain
    exp_date = datetime.now() + timedelta(seconds=5)
    domain = db.Domain(userId="109550028",
                       domain="test-expire.nycu-dev.me",
                       regDate=datetime.now(),
                       expDate=datetime.now(),
                       status=1)
    session.add(domain)
    session.commit()
    # Waiting for expiring
    time.sleep(10)
    recycle()
    assert dnsService.get_domain("test-expire.nycu-dev.me") == None

import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pydig

from models import Domains, Records, Users, Glues, Dnskeys, db, DDNS
from services import DNSService
import config


ddns = DDNS(logging, "/etc/ddnskey.conf", "172.21.21.3", "nycu-dev.me")

resolver = pydig.Resolver(
    executable='/usr/bin/dig',
    nameservers=[
        '172.21.21.3'
    ],
)

sql_engine = create_engine('sqlite:///:memory:')
db.Base.metadata.create_all(sql_engine)
Session = sessionmaker(bind=sql_engine)
session = Session()

users = Users(sql_engine)
domains = Domains(sql_engine)
records = Records(sql_engine)
glues = Glues(sql_engine)
dnskeys = Dnskeys(sql_engine)

dnsService = DNSService(logging, users, domains, records, glues, dnskeys, ddns, config.HOST_DOMAINS)

testdata = [("test-reg.nycu-dev.me", 'A', "140.113.89.64", 5),
            ("test-reg.nycu-dev.me", 'A', "140.113.64.89", 5)]
answer = {"140.113.89.64", "140.113.64.89"}

def test_sql_trigger():
    dnsService.register_domain("109550028", "test-reg.nycu-dev.me")
    for testcase in testdata:
        dnsService.add_record(*testcase)
    time.sleep(10)
    assert set(resolver.query("test-reg.nycu-dev.me", 'A')) == answer
    dnsService.release_domain("test-reg.nycu-dev.me")
    dnsService.register_domain("109550028", "test-reg.nycu-dev.me")
    time.sleep(10)
    assert set(resolver.query("test-reg.nycu-dev.me", 'A')) == set()

    

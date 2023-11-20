from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
import pydig
import time

from models import Domains, Records, Users, db, DDNS
from services import AuthService, DNSService
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

authService = AuthService(logging, config.JWT_SECRET, users)
dnsService = DNSService(logging, users, domains, records, ddns)

testdata = [("test.nycu-dev.me", 'A', "140.113.89.64", 5),
            ("test.nycu-dev.me", 'A', "140.113.64.89", 5)]
answer = {"140.113.89.64", "140.113.64.89"}

def test_domain_register():
    dnsService.register_domain("109550028", "test.nycu-dev.me")
    for testcase in testdata:
        dnsService.add_record(*testcase)
    time.sleep(10)
    assert set(resolver.query("test.nycu-dev.me", 'A')) == answer
    dnsService.release_domain("test.nycu-dev.me")
    dnsService.register_domain("109550028", "test")
    time.sleep(10)
    assert set(resolver.query("test.nycu-dev.me", 'A')) == set()

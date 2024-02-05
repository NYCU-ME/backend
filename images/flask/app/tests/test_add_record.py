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

def test_duplicated_record():
    dnsService.register_domain("109550028", "test-add-dup-rec.nycu-dev.me")
    dnsService.add_record("test-add-dup-rec.nycu-dev.me", 'A', "140.113.64.89", 5)
    try:
        dnsService.add_record("test-add-dup-rec.nycu-dev.me", 'A', "140.113.64.89", 5)
        assert 0
    except Exception:
        assert 1
    dnsService.release_domain("test-add-dup-rec.nycu-dev.me")

def test_glue_record():
    dnsService.register_domain("109550028", "test-glue.nycu-dev.me")

    dnsService.add_glue_record("test-glue.nycu-dev.me", "abc", "A", "1.1.1.1", 5)
    time.sleep(5)
    assert set(resolver.query("abc.test-glue.nycu-dev.me", 'A')) == {"1.1.1.1"}

    dnsService.del_glue_record("test-glue.nycu-dev.me", "abc", "A", "1.1.1.1")
    time.sleep(5)
    assert set(resolver.query("abc.test-glue.nycu-dev.me", 'A')) == set()

    # check if glue record is be removed after domain released
    dnsService.add_glue_record("test-glue.nycu-dev.me", "abc", "A", "1.1.1.1", 5)
    dnsService.release_domain("test-glue.nycu-dev.me")
    time.sleep(5)
    assert set(resolver.query("abc.test-glue.nycu-dev.me", 'A')) == set()

def test_add_dnskey_record():
    dnsService.register_domain("109550028", "test-dnskey.nycu-dev.me")
    dnsService.add_dnssec_key(
	    "test-dnskey.nycu-dev.me", 
	    "257", 
            "13", 
            "oGPBfdLt+oJa6pAnDHtNcZ61d5MWfeocmxdkBI7YuS8D5MOMxLtc7Kyr " +
	    "ItibqhKrrBh4m73uy4N6fRhf2e5Bug==",
	    5)
    time.sleep(5)
    assert set(resolver.query("test-dnskey.nycu-dev.me", 'dnskey')) == {
            "257 3 13 oGPBfdLt+oJa6pAnDHtNcZ61d5MWfeocmxdkBI7YuS8D5MOMxLtc7Kyr " +
            "ItibqhKrrBh4m73uy4N6fRhf2e5Bug=="
    }
    dnsService.del_dnssec_key(
	    "test-dnskey.nycu-dev.me", 
	    "257", 
            "13", 
            "oGPBfdLt+oJa6pAnDHtNcZ61d5MWfeocmxdkBI7YuS8D5MOMxLtc7Kyr " +
	    "ItibqhKrrBh4m73uy4N6fRhf2e5Bug==")
    time.sleep(5)
    assert set(resolver.query("test-dnskey.nycu-dev.me", 'dnskey')) == set()

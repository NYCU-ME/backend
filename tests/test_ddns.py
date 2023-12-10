import logging
import time
import pydig
import models.ddns

ddns = models.ddns.DDNS(logging, "/etc/ddnskey.conf", "172.21.21.3", "nycu-dev.me")
resolver = pydig.Resolver(
    executable='/usr/bin/dig',
    nameservers=[
        '172.21.21.3'
    ],
)

testdata_A = [("test-ddns.nycu-dev.me", 'A', "140.113.89.64", 5),
              ("test-ddns.nycu-dev.me", 'A', "140.113.64.89", 5),
              ("test2-ddns.nycu-dev.me", 'A', "140.113.69.69", 86400),
]
testdata_mx = ("test-ddns.nycu-dev.me", 'MX', "test-ddns.nycu-dev.me", 5)

def test_add_a_record():
    domains = {}
    for testcase in testdata_A:
        ddns.add_record(*testcase)
        if testcase[0] not in domains:
            domains[testcase[0]] = set()
        domains[testcase[0]].add(testcase[2])
    time.sleep(5)
    for domain, expected_value in domains.items():
        assert set(resolver.query(domain, 'A')) == expected_value
    for testcase in testdata_A:
        ddns.del_record(*testcase[:-1])
    time.sleep(5)
    for domain in domains:
        assert not resolver.query(domain, 'A')

def test_add_mx_record():
    ddns.add_record(*testdata_mx)
    time.sleep(5)
    assert set(resolver.query(testdata_mx[0], 'MX')) == {"10 test-ddns.nycu-dev.me."}
    ddns.del_record(*testdata_mx[:-1])
    time.sleep(5)
    assert set(resolver.query(testdata_mx[0], 'MX')) == set()

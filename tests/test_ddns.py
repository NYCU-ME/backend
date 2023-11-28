import models.ddns
import logging
import pydig
import time

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

def test_add_A_record():
    domains = {}
    for testcase in testdata_A:
        ddns.add_record(*testcase);
        if testcase[0] not in domains:
            domains[testcase[0]] = set()
        domains[testcase[0]].add(testcase[2]);
    time.sleep(5)
    for domain in domains:
        assert set(resolver.query(domain, 'A')) == domains[domain]
    for testcase in testdata_A:
        ddns.del_record(*testcase[:-1])
    time.sleep(5)
    for domain in domains:
        assert resolver.query(domain, 'A') == []

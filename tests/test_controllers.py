import json
import time
import requests
import pydig
from .test_common import get_headers, URL_BASE




resolver = pydig.Resolver(
    executable='/usr/bin/dig',
    nameservers=[
        '172.21.21.3'
    ],
)

def test_register_and_release_domain():
    headers = get_headers("109550004")
    # Register domains
    response = requests.post(URL_BASE + "domains/me/nycu-dev/test-route-reg1", headers = headers)
    assert response.status_code == 200
    response = requests.post(URL_BASE + "domains/me/nycu-dev/test-route-reg2", headers = headers)
    assert response.status_code == 200

    # check if the entries exist
    response = requests.get(URL_BASE + "/whoami/", headers = headers)
    domains = json.loads(response.text)['domains']
    assert {domain['domain'] for domain in domains} == {'test-route-reg1.nycu-dev.me', 'test-route-reg2.nycu-dev.me'}

    # release the domains
    response = requests.delete(URL_BASE + "domains/me/nycu-dev/test-route-reg1", headers = headers)
    assert response.status_code == 200
    response = requests.delete(URL_BASE + "domains/me/nycu-dev/test-route-reg2", headers = headers)
    assert response.status_code == 200

    # check if the domain were released
    response = requests.get(URL_BASE + "/whoami/", headers = headers)
    domains = json.loads(response.text)['domains']
    assert {domain['domain'] for domain in domains} == set()

def test_add_and_delete_records():
    headers = get_headers("109550028")
    # Register domains
    response = requests.post(URL_BASE + "domains/me/nycu-dev/test-route-rec", headers = headers)
    assert response.status_code == 200
    # Add records
    response = requests.post(URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.89.64", headers = headers)
    assert response.status_code == 200
    response = requests.post(URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.64.89", headers = headers)
    assert response.status_code == 200
    # Check the result
    time.sleep(10)
    assert set(resolver.query("test-route-rec.nycu-dev.me", 'A')) == {"140.113.89.64", "140.113.64.89"}
    # Remove the records
    response = requests.delete(URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.89.64", headers = headers)
    assert response.status_code == 200
    response = requests.delete(URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.64.89", headers = headers)
    assert response.status_code == 200

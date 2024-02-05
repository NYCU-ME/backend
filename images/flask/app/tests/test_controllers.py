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
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-route-reg1",
            headers = headers,
            timeout=10
    )

    assert response.status_code == 200
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-route-reg2",
            headers = headers,
            timeout=10
    )

    assert response.status_code == 200

    # check if the entries exist
    response = requests.get(
            URL_BASE + "/whoami/",
            headers = headers,
            timeout=10
    )
    domains = json.loads(response.text)['domains']
    assert {domain['domain'] for domain in domains} == {'test-route-reg1.nycu-dev.me',
                                                        'test-route-reg2.nycu-dev.me'}

    # release the domains
    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-route-reg1",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-route-reg2",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

    # check if the domain were released
    response = requests.get(
            URL_BASE + "/whoami/",
            headers = headers,
            timeout=10
    )
    domains = json.loads(response.text)['domains']
    assert {domain['domain'] for domain in domains} == set()

def test_get_domain_by_id():
    headers = get_headers("0716023")
    # Register domain
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-domain-id",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

    response = requests.get(
            URL_BASE + "whoami/",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    idx = json.loads(response.text)['domains'][0]['id']
    # Because of the parallel, we cannot determine
    # which one would be the answer.
    response = requests.get(
        URL_BASE + f"domain/{idx}",
        headers = headers,
        timeout=10
    )
    assert response.status_code == 200
    domain_name = json.loads(response.text)['domain']['domain']
    assert domain_name == "test-domain-id.nycu-dev.me"

    # Release domain
    response = requests.delete(
        URL_BASE + "domains/me/nycu-dev/test-domain-id",
        headers = headers,
        timeout=10
    )
    assert response.status_code == 200

def test_add_and_delete_records():
    headers = get_headers("109550028")
    # Register domains
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-route-rec",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    # Add records
    response = requests.post(
            URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.89.64",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    response = requests.post(
            URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.64.89",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    # Check the result
    time.sleep(10)
    assert set(resolver.query("test-route-rec.nycu-dev.me", 'A')) == {"140.113.89.64",
                                                                      "140.113.64.89"}
    # Remove the records
    response = requests.delete(
        URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.89.64",
        headers = headers,
        timeout=10
    )
    assert response.status_code == 200
    response = requests.delete(
        URL_BASE + "ddns/me/nycu-dev/test-route-rec/records/A/140.113.64.89",
        headers = headers,
        timeout=10
    )
    assert response.status_code == 200

def test_auto_delete_glue_record():

    headers = get_headers("110550029")

    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-glue-rec",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

    response = requests.post(
            URL_BASE + "glue/me/nycu-dev/test-glue-rec/records/abc/A/1.1.1.1",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

    response = requests.delete(
            URL_BASE + "glue/me/nycu-dev/test-glue-rec/records/abc/A/1.1.1.1",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-glue-rec",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

def test_add_ttl():

    headers = get_headers("109550032")

    def test_ttl(ttl, answer):
        # Add record for ttl 10
        response = requests.post(
                URL_BASE + "ddns/me/nycu-dev/test-ttl1/records/A/140.113.89.64",
                json = {'ttl': ttl},
                headers = headers,
                timeout=10
        )
        assert response.status_code == 200
        response = requests.get(
                URL_BASE + "whoami/",
                headers = headers,
                timeout=10
        )
        assert response.status_code == 200
        for domain in json.loads(response.text)['domains']:
            if domain['domain'] == 'test-ttl1.nycu-dev.me':
                assert domain['records'][0][3] == answer
        response = requests.delete(
                URL_BASE + "ddns/me/nycu-dev/test-ttl1/records/A/140.113.89.64",
                headers = headers,
                timeout=10
        )

    # Register domains
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-ttl1",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

    test_ttl(1, 5)
    test_ttl(10, 10)
    test_ttl(86401, 5)
    test_ttl("random_string", 5)
    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-ttl1",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200

def test_dnssec():
    headers = get_headers("10360874")

    # Register domains
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-dnssec",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    # Add KSK
    response = requests.post(
            URL_BASE + "dnssec/me/nycu-dev/test-dnssec/records/",
            json = {
                "flag": 257,
                "algorithm": 13,
                'value': (
                       "oGPBfdLt+oJa6pAnDHtNcZ61d5MWfeocmxdkBI7YuS8D5MOMxLtc7Kyr "+ 
                       "ItibqhKrrBh4m73uy4N6fRhf2e5Bug==" 
                ),
                'ttl': 5
            },
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    time.sleep(5)
    assert set(resolver.query("test-dnssec.nycu-dev.me", 'dnskey')) == {
            "257 3 13 oGPBfdLt+oJa6pAnDHtNcZ61d5MWfeocmxdkBI7YuS8D5MOMxLtc7Kyr " +
            "ItibqhKrrBh4m73uy4N6fRhf2e5Bug=="
    }
    # Del KSK
    response = requests.delete(
            URL_BASE + "dnssec/me/nycu-dev/test-dnssec/records/",
            json = {
                "flag": 257,
                "algorithm": 13,
                'value': (
                       "oGPBfdLt+oJa6pAnDHtNcZ61d5MWfeocmxdkBI7YuS8D5MOMxLtc7Kyr "+ 
                       "ItibqhKrrBh4m73uy4N6fRhf2e5Bug==" 
                )
            },
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    time.sleep(5)
    assert set(resolver.query("test-dnssec.nycu-dev.me", 'dnskey')) == set()
    # Test recycling
    response = requests.post(
            URL_BASE + "dnssec/me/nycu-dev/test-dnssec/records/",
            json = {
                "flag": 257,
                "algorithm": 13,
                'value': (
                       "oGPBfdLt+oJa6pAnDHtNcZ61d5MWfeocmxdkBI7YuS8D5MOMxLtc7Kyr "+ 
                       "ItibqhKrrBh4m73uy4N6fRhf2e5Bug==" 
                ),
                'ttl': 5
            },
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    time.sleep(5)
    assert set(resolver.query("test-dnssec.nycu-dev.me", 'dnskey')) != set()
    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-dnssec",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    time.sleep(5)
    assert set(resolver.query("test-dnssec.nycu-dev.me", 'dnskey')) == set()

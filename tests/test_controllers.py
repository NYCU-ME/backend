import requests
import json
import config
import time


URL_BASE = "http://172.21.21.4:8000/"

response = requests.get(URL_BASE + "test_auth/")
token = json.loads(response.text)['token']
headers = {'Authorization': 'Bearer ' + token}

def test_register_domain():
    response = requests.post(URL_BASE + "domains/me/nycu-dev/test-route-reg", headers = headers)
    assert response.status_code == 200
    response = requests.get(URL_BASE + "/whoami/", headers = headers)
    domains = json.loads(response.text)['domains']
    assert {domain['domain'] for domain in domains} == {'test-route-reg.nycu-dev.me'}

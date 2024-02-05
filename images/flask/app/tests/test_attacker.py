import requests
from .test_common import get_headers, URL_BASE

def test_permission():
    h04 = get_headers("109550004")
    h28 = get_headers("109550028")

    # Register domain
    response = requests.post(
                URL_BASE + "domains/me/nycu-dev/test-permission1",
                headers = h28,
                timeout=10
    )
    assert response.status_code == 200
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-permission1",
            headers = h04,
            timeout=10
    )
    assert response.status_code == 403
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-permission1",
            timeout=10
    )
    assert response.status_code == 401

    # Add record
    response = requests.post(
            URL_BASE + "ddns/me/nycu-dev/test-permission1/records/A/140.113.89.64",
            timeout=10
    )
    assert response.status_code == 401
    response = requests.post(
            URL_BASE + "ddns/me/nycu-dev/test-permission1/records/A/140.113.89.64",
            headers = h04,
            timeout=10
    )
    assert response.status_code == 403
    response = requests.post(
            URL_BASE + "ddns/me/nycu-dev/test-permission1/records/A/140.113.89.64",
            headers = h28,
            timeout=10
    )
    assert response.status_code == 200

    # Delete record
    response = requests.delete(
            URL_BASE + "ddns/me/nycu-dev/test-permission1/records/A/140.113.89.64",
            timeout=10
    )
    assert response.status_code == 401
    response = requests.delete(
            URL_BASE + "ddns/me/nycu-dev/test-permission1/records/A/140.113.89.64",
            headers = h04,
            timeout=10
    )
    assert response.status_code == 403
    response = requests.delete(
            URL_BASE + "ddns/me/nycu-dev/test-permission1/records/A/140.113.89.64",
            headers = h28,
            timeout=10
    )
    assert response.status_code == 200

    # Release domain
    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-permission1",
            timeout=10
    )
    assert response.status_code == 401
    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-permission1",
            headers = h04,
            timeout=10
    )
    assert response.status_code == 403
    response = requests.delete(
            URL_BASE + "domains/me/nycu-dev/test-permission1",
            headers = h28,
            timeout=10
    )
    assert response.status_code == 200

def test_invalid_operation():
    headers = get_headers("109550032")
    response = requests.post(
            URL_BASE + "domains/me/nycu-dev/test-attack",
            headers = headers,
            timeout=10
    )
    assert response.status_code == 200
    response = requests.post(
            URL_BASE + "ddns/me/nycu-dev/test-permission1/records/TXT/attack \
                        message%0Ans2 A 103.179.29.12",
            timeout=10
    )
    print(response.status_code)

import requests
from .test_common import URL_BASE

def test_email_login():
    response = requests.post(
            URL_BASE + "login_email",
            json = {'email': "10360874@me.mcu.edu.tw"},
            timeout=10
    )
    print(response.text)
    assert response.status_code == 200

    response = requests.post(
            URL_BASE + "login_email",
            json = {'email': "rogerdeng92@gmail.com"},
            timeout=10
    )
    assert response.status_code == 400

    response = requests.post(
            URL_BASE + "login_email",
            json = {'email': "lin.cs09@nycu.edu.tw"},
            timeout=10
    )
    assert response.status_code == 400

    response = requests.post(
            URL_BASE + "login_email",
            json = {'email': "ccy@cs.nctu.edu.tw"},
            timeout=10
    )
    assert response.status_code == 400

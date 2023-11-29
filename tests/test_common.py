import requests
import json

URL_BASE = "http://172.21.21.4:8000/"

def get_headers(uid):
    data = {
            "email": "lin.cs09@nycu.edu.tw",
            "username": uid
    }
    response = requests.get(URL_BASE + "test_auth/", json = data)
    token = json.loads(response.text)['token']
    headers = {'Authorization': f'Bearer {token}'}
    return headers
import json
import requests
from .test_common import get_headers, URL_BASE

def test_user_count():
    get_headers("0716023")
    get_headers("10360874")
    get_headers("109550004")
    get_headers("109550028")
    get_headers("109550032")

    response = requests.get(
            URL_BASE + "metrics/",
            timeout=10
    )
    num_of_user = json.loads(response.text)['num_of_user']
    assert num_of_user >= 5

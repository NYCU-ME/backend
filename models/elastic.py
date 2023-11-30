import requests
import json
import config

class Elastic():

    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password

    def query_logs_count_by_date(self, domain, date):
        url = f"http://{self.server}:9200/fluentd.named.dns/_search?pretty=true"
        headers = {"Content-Type": "application/json"}
        auth = (self.user, self.password)
        data = {
            "size": 0, 
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": f"*{domain}*"}},
                        {"range": {"log_date": {"gte": date, "lte": date}}}
                    ]
                }
            }
        }

        response = requests.get(url, headers=headers, auth=auth, data=json.dumps(data))
        response_json = response.json()

        return response_json.get('hits', {}).get('total', {}).get('value', 0)



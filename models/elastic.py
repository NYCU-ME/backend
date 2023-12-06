from elasticsearch import Elasticsearch
import logging
class Elastic():

    def __init__(self, server, user, password):
        self.elastic = Elasticsearch(
                server,
                http_auth=(user, password)
        )

    def query(self, domain, date):
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"wildcard": {"log": f"(*.{domain})"}},
                        {"wildcard": {"log": f"({domain})"}}
                    ],
                    "filter": {
                        "range": {
                            "@timestamp": {
                                "gte": f"{date}T00:00:00",
                                "lt": f"{date}T23:59:59"
                            }
                        }
                    }
                }
            }
       
        count_response = self.elastic.count(index="fluentd.named.dns", body=query)
        return count_response['count']
    


from elasticsearch import Elasticsearch

class Elastic():

    def __init__(self, server, user, password):
        self.elastic = Elasticsearch(
                server,
                http_auth=(user, password)
        )

    def query(self, domain, date):
        query = {
            "query": {
                "constant_score": {
                    "filter": {
                        "bool": {
                            "must": {
                                "match": {
                                    "log": f"{domain}"
                                }
                            },
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
                }
            }
        }
        count_response = self.elastic.count(body=query, index="fluentd.named.dns") # pylint: disable=unexpected-keyword-arg
        return count_response['count']

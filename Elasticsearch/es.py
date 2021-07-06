from datetime import datetime
from elasticsearch import Elasticsearch
import json

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
doc = {
    'author': 'author_name',
    'text': 'Interesting content...',
    'timestamp': datetime.now(),
}
result = es.index(index="test-index", id=1, body=doc)
print(result['result'])
print("indexing")
print(json.dumps(result, indent=4))

result = es.get(index="test-index", id=1)
print("Get")
print(json.dumps(result, indent=4))

result = es.indices.refresh(index="test-index")
print("Refresh")
print(json.dumps(result, indent=4))

res = es.search(
    index="test-index",
    body={"query": {"match_all": {}}}
)
print("Got %d Hits:" % res['hits']['total']['value'])
for hit in res['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])

doc = {
    'author': 'author_name',
    'text': 'Interesting modified content...',
    'timestamp': datetime.now(),
}
# res = es.update(index="test-index", id=1, body=doc)
# print("Updated")
# print(json.dumps(result, indent=4))

# es.delete(index="test-index", id=1)


# Fetching all ids
from elasticsearch_dsl import Search
s = Search(using=es, index="test-index", doc_type="_doc")
ids = [h.meta.id for h in s.scan()]
print(ids)

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import re

from itemadapter import ItemAdapter

from elasticsearch import Elasticsearch, helpers

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
es.indices.create(index='ted-index2', body={
    'mappings': {
        'properties': {
            "title": {"type": "text"},
            "talk-description": {"type": "text"},
            "viewed_count": {"type": "integer"},
            "duration": {"type": "integer"},
            "recorded_at": {"type": "date"},
            "tags": {"type": "keyword"},
            "speakers": {
                "properties": {
                    "name":  {"type": "text"},
                    "description":  {"type": "text"}
                }
            },
        }
    }
})


def generate_unique_id_from_title(title):
    """
    Responsibility: Generate a unique id from input string.
    """
    regex = re.compile('[^a-zA-Z0-9]')
    m = hashlib.md5()
    title = title.lower()
    title = regex.sub('', title)
    m.update(title.encode("utf-8"))
    return m.hexdigest()


class ElasticsearchPipeline:
    actions = []
    counter = 0

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):

        action = {
            "_index": "ted-index2",
            'op_type': 'create',
            "_id": generate_unique_id_from_title(item["title"]),
            "_source": item
        }

        self.actions.append(action)

        self.counter += 1
        print(f"Crawled {self.counter} talks")

        if len(self.actions) == 10:
            helpers.bulk(es, self.actions, index='ted-index2')
            self.actions.clear()
            print(f"Added {self.counter} items")

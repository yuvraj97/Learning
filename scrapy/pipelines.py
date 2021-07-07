# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from elasticsearch import Elasticsearch, helpers


class ElasticsearchPipeline:
    actions = []

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        # print(spider.settings)
        es = Elasticsearch(
            [{'host': spider.settings["ELASTICSEARCH_HOST"], 'port': spider.settings["ELASTICSEARCH_PORT"]}])
        action = {
            "_index": "ted-index",
            'op_type': 'create',
            "_id": item['doc_id'],
            "_source": item
        }
        self.actions.append(action)

        if len(self.actions) == 10:
            helpers.bulk(es, self.actions, index='ted')
            self.actions.clear()

import hashlib
import re

import scrapy
from elasticsearch import Elasticsearch
import json

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

class TedSpider(scrapy.Spider):
    name = "test"

    def start_requests(self):
        urls = [
            'https://www.ted.com/talks/clover_hogan_what_to_do_when_climate_change_feels_unstoppable',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("----------------------")
        print()
        print()

        items = response.xpath("//script[contains(., 'whotheyare')]/text()")
        txt: str = items.extract_first()
        data = json.loads(txt[txt.index("{"): len(txt)-1])["__INITIAL_DATA__"]

        speakers = {}
        for speaker in data["speakers"]:
            speakers["name"] = speaker["firstname"] + " " + speaker["lastname"]
            speakers["description"] = speaker["whotheyare"]

        title = data["name"]
        description = data["description"]
        viewed_count = data["viewed_count"]

        print(speakers, title, viewed_count)
        print(description)

        result = es.index(
            index="ted-test-index",
            doc_type="title",
            id=self.generate_unique_id_from_title(title),
            body={"title": data["name"]}
        )
        print("title", result['result'])

        result = es.index(
            index="ted-test-index",
            doc_type="description",
            id=self.generate_unique_id_from_title(title),
            body={"description": data["description"]}
        )
        print("description", result['result'])

        result = es.index(
            index="ted-test-index",
            doc_type="viewed_count",
            id=self.generate_unique_id_from_title(title),
            body={"viewed_count": data["viewed_count"]}
        )
        print("viewed_count", result['result'])

        result = es.index(
            index="ted-test-index",
            doc_type="speakers",
            id=self.generate_unique_id_from_title(title),
            body=speakers
        )
        print("speakers", result['result'])

        print()
        print("----------------------")

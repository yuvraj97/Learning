import json
import scrapy
from datetime import datetime
from elasticsearch import Elasticsearch
import json

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


class TedSpider(scrapy.Spider):
    name = "ted"

    def start_requests(self):
        urls = [
            'https://www.ted.com/topics',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for link in response.css("a"):
            topic_href = link.attrib['href']
            if "/topics/" not in topic_href:
                continue
            if not topic_href.startswith("https"):
                topic_href = response.urljoin(topic_href)
            yield scrapy.Request(topic_href, callback=self.process_topic)

    def process_topic(self, response):
        for link in response.css("a"):
            talk_href = link.attrib['href']
            if "/talks/" not in talk_href:
                continue
            if not talk_href.startswith("https"):
                talk_href = response.urljoin(talk_href)
            yield scrapy.Request(talk_href, callback=self.process_talk)

    def process_talk(self, response):
        items = response.xpath("//script[contains(., 'whotheyare')]/text()")
        txt: str = items.extract_first()
        data = json.loads(txt[txt.index("{"): len(txt) - 1])
        speakers = []
        for speaker in data["__INITIAL_DATA__"]["speakers"]:
            speakers.append({
                "name": speaker["firstname"] + " " + speaker["lastname"],
                "description": speaker["whotheyare"]
            })

        refinedData = {
            "viewed_count": data["__INITIAL_DATA__"]["viewed_count"],
            "talk": {
                "lang": data["__INITIAL_DATA__"]["requested_language_english_name"],
                "description": data["__INITIAL_DATA__"]["description"],
                "title": data["__INITIAL_DATA__"]["name"]
            },
            "speakers": speakers,
        }

        result = es.index(index="ted-index", id=hash(refinedData["talk"]["title"]), body=refinedData)
        print(result['result'])



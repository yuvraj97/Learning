import scrapy
import json


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
        data = json.loads(txt[txt.index("{"): len(txt) - 1])["__INITIAL_DATA__"]

        speakers = []
        for speaker in data["speakers"]:
            speakers.append({
                "name": speaker["firstname"] + " " + speaker["lastname"],
                "description": speaker["whotheyare"]
            })

        yield {
            "title": data["name"],  # { "type": "text" }
            "talk-description": data["description"],  # { "type": "text" }
            "viewed_count": data["viewed_count"],  # { "type": "integer" }
            "speakers": speakers,   '''  "properties": {
                                              "name":  { "type": "text" },
                                              "description":  { "type": "text" }
                                          }
                                    '''
            "duration": data["talks"][0]["duration"],  # { "type": "integer" }
            "recorded_at": data["talks"][0]["recorded_at"],  # { "type": "date" }
            "tags": data["talks"][0]["tags"],  # { "type": "keyword" }
        }

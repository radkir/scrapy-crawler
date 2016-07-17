# -*- coding: utf-8 -*-
import scrapy

from LotI.items import LotiItem

class PropertySpider(scrapy.Spider):
    name = "property"
    allowed_domains = ["quoka.de"]
    start_urls = (
        'http://www.quoka.de/immobilien/bueros-gewerbeflaechen/',
    )

    def parse(self, response):
        for href in response.xpath('//div[@id="ResultListData"]').xpath('//a[@class="qaheadline item fn"]/@href'):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)


    def parse_dir_contents(self, response):
        for sel in response.xpath('//div[@id="ResultListData"]').xpath('//li'):
            item = LotiItem()
            item['desc'] = sel.xpath('//div[@class="description"]').extract()
            yield item

# -*- coding: utf-8 -*-
import scrapy
import httplib
import re

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
        item = LotiItem()

        item['url'] = response.url

        head = response.xpath('//div[@class="headline"]')
        item['uberschrift'] = head.xpath('//h1[@itemprop="name"]/text()').extract()

        price = response.xpath('//div[@class="price has-type"]')
        item['kaufpreis'] = price.xpath('strong/span/text()').re(r'(.*[0-9]+)')

        description = response.xpath('//div[@itemprop="description"]')
        item['beschreibung'] = description.xpath('text()').extract()

        telephone = response.xpath('//ul[@class="contacts"]')
        request = telephone.xpath('li/span/a[@id="dspphone1"]/@onclick').re(r'/ajax.*[0-9]')
        conn = httplib.HTTPSConnection("www.quoka.de")
        if request != []:
            conn.request("GET", request[0])
            r1 = conn.getresponse()
            data1 = r1.read()
            number = re.sub('[^0-9]*','', data1)
            item['telefon'] = number

        details = response.xpath('//div[@itemprop="offerDetails"]')
        item['plz'] = details.xpath('div/strong/span/span/span[@class="postal-code"]/text()').extract()
        item['stadt'] = details.xpath('div/strong/span/a/span[@class="locality"]/text()').extract()
        date = details.xpath('div[@class="date-and-clicks"]/text()').re(r'(.*[0-9]+)')
        if date == []:
            date = details.xpath('div[@class="date-and-clicks"]/text()').re(r'(.*e+.[a-z]*)')
        item['erstellungsdatum'] = date
        item['obid'] = details.xpath('div[@class="date-and-clicks"]/strong/text()').re(r'(.*[0-9]+)')
        print(item)
      #  yield item

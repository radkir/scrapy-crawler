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
        item = LotiItem()

        head = response.xpath('//div[@class="headline"]')
        item['uberschrift'] = head.xpath('//h1[@itemprop="name"]/text()').extract()

        price = response.xpath('//div[@class="price has-type"]')
        item['kaufpreis'] = price.xpath('strong/span/text()').extract()

        description = response.xpath('//div[@itemprop="description"]')
        item['beschreibung'] = description.xpath('text()').extract()

        telephone = response.xpath('//ul[@class="contacts"]')
    #    item['telefon'] = telephone.xpath('').extract()

        details = response.xpath('//div[@itemprop="offerDetails"]')
        item['plz'] = details.xpath('div/strong/span/span/span[@class="postal-code"]/text()').extract()
        item['stadt'] = details.xpath('div/strong/span/a/span[@class="locality"]/text()').extract()
     #   item['obid'] = details.xpath('').extract()
    #    item['erstellungsdatum'] = details.xpath('').extract()
        print(item)
      #  yield item

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LotiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    uberschrift = scrapy.Field()
    kaufpreis = scrapy.Field()
    telefon = scrapy.Field()
    plz = scrapy.Field()
    stadt = scrapy.Field()
    obid = scrapy.Field()
    beschreibung = scrapy.Field()
    erstellungsdatum = scrapy.Field()
    url = scrapy.Field()
    gewerblich = scrapy.Field()
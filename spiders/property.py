# -*- coding: utf-8 -*-
import scrapy
import httplib
import re
import datetime

from datetime import timedelta
from LotI.items import LotiItem
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Boersen_ID = db.Column(db.Integer)
    OBID = db.Column(db.Integer)
    erzeugt_am = db.Column(db.Integer)
    Anbieter_ID = db.Column(db.Integer)
    Stadt = db.Column(db.String(150))
    PLZ = db.Column(db.String(10))
    Uberschrift = db.Column(db.String(500))
    Beschreibung = db.Column(db.String(15000))
    Kaufpreis = db.Column(db.Integer)
    Monat = db.Column(db.Integer)
    url = db.Column(db.String(1000))
    Telefon = db.Column(db.Integer)
    Erstellungsdatum = db.Column(db.Integer)
    Gewerblich = db.Column(db.Integer)

    def __init__(self, Boersen_ID, OBID, erzeugt_am, Anbieter_ID, Stadt,
                 PLZ, Uberschrift, Beschreibung, Kaufpreis, Monat, url,
                 Telefon, Erstellungsdatum, Gewerblich
                 ):
        self.Boersen_ID = Boersen_ID
        self.OBID = OBID
        self.erzeugt_am = erzeugt_am
        self.Anbieter_ID = Anbieter_ID
        self.Stadt = Stadt
        self.PLZ = PLZ
        self.Uberschrift = Uberschrift
        self.Beschreibung = Beschreibung
        self.Kaufpreis = Kaufpreis
        self.Monat = Monat
        self.url = url
        self.Telefon = Telefon
        self.Erstellungsdatum = Erstellungsdatum
        self.Gewerblich = Gewerblich

db.create_all()

class PropertySpider(scrapy.Spider):
    name = "property"
    allowed_domains = ["quoka.de"]
    start_urls = (
        'http://www.quoka.de/immobilien/bueros-gewerbeflaechen/',
    )

    def parse(self, response):
        for href in response.xpath('//div[@id="ResultListData"]'):
            dodo = response.xpath('//a[@class="qaheadline"]').extract()
            print(dodo)
         #('//a[@class="qaheadline item fn"]/@href'):'//a[@class="qaheadline"]'
            if href.xpath('//a[@class="qaheadline"]/h3/text()') == []:
                for ref in response.xpath('//a[@class="qaheadline item fn"]/@href'):
                   url = response.urljoin(ref.extract())
                   yield scrapy.Request(url, callback=self.parse_dir_contents)
            else:
                for ref in response.xpath('//a[@class="qaheadline"]'):
                  item = LotiItem()
                #  item['uberschrift'] =
                  print("item")





    def parse_dir_contents(self, response):
        item = LotiItem()

        item['url'] = response.url

        head = response.xpath('//h1[@itemprop="name"]/text()').extract()
        title = re.sub(u'[^a-z\.,\ \-A-Z]*', u'', head[0])
        item['uberschrift'] = title

        price = response.xpath('//div[@class="price has-type"]/strong/span/text()').re(r'(.*[0-9]+)')
        if price != []:
            amount = re.sub(u'(\.)*', u'', price[0])
            amount = re.sub(u',', u'.', amount)
            item['kaufpreis'] = float(amount)
        else:
            item['kaufpreis'] = 0

        descriptionbox = response.xpath('//div[@itemprop="description"]')
        descriptionraw = '.'.join(descriptionbox.xpath('text()').extract())
        description = re.sub(u'[^a-z A-Z\.,]*', u'', descriptionraw)
        item['beschreibung'] = description

        telephone = response.xpath('//ul[@class="contacts"]')
        request = telephone.xpath('li/span/a[@id="dspphone1"]/@onclick').re(r'/ajax.*[0-9]')
        conn = httplib.HTTPSConnection("www.quoka.de")
        if request != []:
            conn.request("GET", request[0])
            r1 = conn.getresponse()
            data1 = r1.read()
            number = re.sub('[^0-9]*','', data1)
            item['telefon'] = int(number)
        else:
            item['telefon'] = 0

        detailsbox = response.xpath('//div[@itemprop="offerDetails"]')
        postcode = detailsbox.xpath('div/strong/span/span/span[@class="postal-code"]/text()').extract()
        item['plz'] = postcode[0]

        city = detailsbox.xpath('div/strong/span/a/span[@class="locality"]/text()').extract()
        item['stadt'] = city[0]

        date = detailsbox.xpath('div[@class="date-and-clicks"]/text()').re(r'(.*[0-9]+)')
        if date == []:
            date = detailsbox.xpath('div[@class="date-and-clicks"]/text()').re_first(r'([A-Z]+[a-z]*)')
            now = datetime.datetime.now()
            if date == u'Gestern':
                dday = timedelta(days=1)
                ddate = now - dday
                fdate = int(ddate.strftime("%d%m%Y"))
            else:
                fdate = int(now.strftime("%d%m%Y"))
        else:
            fdate = int(re.sub(u'[.]*', u'', date[0]))
        item['erstellungsdatum'] = fdate

        prid = detailsbox.xpath('div[@class="date-and-clicks"]/strong/text()').re(r'(.*[0-9]+)')
        item['obid'] = int(prid[0])
        print(item)
        db.session.add(item)
      #  yield item

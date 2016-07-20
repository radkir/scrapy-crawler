# -*- coding: utf-8 -*-
import scrapy
import httplib
import re
import datetime

from datetime import timedelta
from LotI.items import LotiItem
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from scrapy.http import FormRequest

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test/result.db'
db = SQLAlchemy(app)

class Line(db.Model):
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

    def spr(self):
        return {
            'id': self.id,
            'Boersen_ID': self.Boersen_ID,
            'OBID': self.OBID,
            'erzeugt_am': self.erzeugt_am,
            'Anbieter_ID' : self.Anbieter_ID,
            'Stadt' : self.Stadt,
            'PLZ' : self.PLZ,
            'Uberschrift' : self.Uberschrift,
            'Beschreibung' : self.Beschreibung,
            'Kaufpreis' : self.Kaufpreis,
            'Monat' : self.Monat
        }

db.create_all()

class PropertySpider(scrapy.Spider):
    name = "property"
    allowed_domains = ["quoka.de"]
    start_urls = (
        'http://www.quoka.de/immobilien/bueros-gewerbeflaechen/',
    )

    def parse(self, response):
        ref = response.xpath('//div[@class="cnt"]/ul/li')

        for href in ref.xpath('.//li/a/@href'):
            str = href.extract()
            if "immobilien/bueros-gewerbeflaechen" in str:
                url = response.urljoin(str)
                yield FormRequest(url, formdata={'classtype': 'of', 'comm': '1'}, callback=self.parse_filtered, meta={'offer': 1})
                yield FormRequest(url, formdata={'classtype': 'of', 'comm': '0'}, callback=self.parse_filtered, meta={'offer': 0})


    def parse_filtered(self, response):
        offer = response.meta['offer']

        for ref in response.xpath('//a[@class="qaheadline item fn"]/@href'):
           url = response.urljoin(ref.extract())
           yield scrapy.Request(url, callback=self.parse_dir_contents, meta={'offer':offer})

        next_page = response.xpath('//li[@class="arr-rgt active"]/a[@class="sem"]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(url, self.parse_filtered, meta={'offer':offer})





    def parse_dir_contents(self, response):
        detailsbox = response.xpath('//div[@itemprop="offerDetails"]')
        prid = detailsbox.xpath('div[@class="date-and-clicks"]/strong/text()').re(r'(.*[0-9]+)')
        obid = int(prid[0])

        query = db.session.query(Line).filter_by(OBID=obid)
        if query.count() == 0:
            offer = response.meta['offer']
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


            postcode = detailsbox.xpath('div/strong/span/span/span[@class="postal-code"]/text()').extract()
            item['plz'] = postcode[0]

            city = detailsbox.xpath('div/strong/span/a/span[@class="locality"]/text()').extract()
            item['stadt'] = city[0]




            date = detailsbox.xpath('div[@class="date-and-clicks"]/text()').re(r'(.*[0-9]+)')
            now = datetime.datetime.now()
            dmy = int(now.strftime("%d%m%Y"))
            if date == []:
                date = detailsbox.xpath('div[@class="date-and-clicks"]/text()').re_first(r'([A-Z]+[a-z]*)')

                if date == u'Gestern':
                    dday = timedelta(days=1)
                    ddate = now - dday
                    fdate = int(ddate.strftime("%d%m%Y"))
                else:
                    fdate = dmy
            else:
                if "vor" in date[0]:
                    dday = timedelta(weeks=24)
                    ddate = now - dday
                    fdate = int(ddate.strftime("%m%Y"))
                else:
                    fdate = int(re.sub(u'[.]*', u'', date[0]))
            item['erstellungsdatum'] = fdate

            item['obid'] = obid
            line = Line(31, item['obid'], dmy, "", item['stadt'], item['plz'], item['uberschrift'],
                        item['beschreibung'], item['kaufpreis'], now.month, item['url'], item['telefon'],
                        item['erstellungsdatum'], offer)

            db.session.add(line)
        else:
            query.update(Gewerblich=1)

        db.session.commit()
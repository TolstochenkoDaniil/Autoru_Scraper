from scrapy import Spider
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.project import get_project_settings
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging
import urllib.parse as url_parse
import re
import os
import pandas as pd

from ..items import CarBriefItem, CarLoader

class Test(Spider):
    name = 'test'
    allowed_domains = ['auto.ru']
    start_urls = ["https://auto.ru/cars/used/sale/skoda/octavia/1100052996-45b9288e/"]
    
    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'test.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        'FEED_EXPORT_FIELDS' : ['ID','title','area','price','offer_price','year','distance',
                      'engine_type','fuel_type','horse_power',
                      'car_type','wheel_type','transmission',
                      'color','city','advert','link','date']
        }
    
    log_dir = get_project_settings().get('LOG_DIR')
    log = os.path.join(log_dir,'test.log')
    
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    logger = logging.getLogger(__name__)

    f_handler = logging.FileHandler(log, mode='w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url,
                          callback=self.parse_details,
                          errback=self.errback_url,
                          dont_filter=True)

    def parse(self, response):    
        self.logger.info("Parsing response {}".format(response.url))             
        selectors = response.xpath('//div[@class=$val]', 
                                   val="ListingItem-module__main")
        
        for selector in selectors:
            yield self.parse_item(selector, response)
            
        # Получение ссылки для перехода на след страницу    
        next_sel = response.css('.ListingPagination-module__next::attr(href)')
        
        # Генератор для извлечения следующей страницы
        for next_page in next_sel.extract():
            yield Request(url_parse.urljoin(response.url, next_page),
                          callback=self.parse,
                          errback=self.errback_url,
                          dont_filter=True)

    def parse_item(self, selector, response):
        carInfoLoader = CarLoader(item=CarBriefItem(), selector=selector)
        area = self.parse_url(response.url)
           
        if selector.css('.ListingItem-module__kmAge::text').get() == 'Новый':
            return [None]
        else:
            carInfoLoader.add_value('area', area)
            carInfoLoader.parse_old()
        
            link_ = carInfoLoader.get_collected_values('link')
            self.logger.info("Selector link is {}".format(link_)) 
        
            # for link in link_:
            #     return Request(link,
            #                   callback=self.parse_details,
            #                   errback=self.errback_url,
            #                   dont_filter=True
            #                   )  
            return carInfoLoader.load_item()
    
    def parse_details(self, response):
        #carInfoLoader = CarLoader(item=item, response=response)
        # self.logger.info("Parsing details for {}".format(carInfoLoader.get_collected_values('ID')))
        self.logger.info("Parsing details in {}".format(response.url))
        date = response.xpath('.//div[@class=$val]//text()',val="bKo4xb5_RtLuJ22JpWtrG__info-item")
        
        if date:
            #self.logger.info("Parsed date {} for car id {}".format(date,carInfoLoader.get_collected_values('ID')))
            self.logger.info(u"Date is {}".format(date[0].get()))
        #carInfoLoader.add_value('date',date)
        
        #return carInfoLoader.load_item()
        return date
    
    def errback_url(self, failure):
        self.logger.error(repr(failure))
        
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError on %s", response.url)
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError on %s", request.url)
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError on %s", request.url)
    
    def parse_url(self, url):
        url_path = url_parse.urlparse(url).path
        match = re.findall('/([a-z]+_[a-z]+)/', url_path)
        
        return match[0]
from scrapy import Spider
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging
import urllib.parse as url_parse
import re
import pandas as pd

from ..items import SpiderTestItem, TestLoader, ModelsLoader, ModelsItem, CarBriefItem, CarLoader

class TestSpider(Spider):
    name = 'test'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/moskovskaya_oblast/cars/skoda/octavia/all/',
                  'https://auto.ru/leningradskaya_oblast/cars/skoda/octavia/all/']
    
    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'test.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        'FEED_EXPORT_FIELDS' : ['ID','title','area','price','offer_price','year','distance',
                      'engine_type','fuel_type','horse_power',
                      'car_type','wheel_type','transmission',
                      'color','city','advert','link']
        }
    
    logger = logging.getLogger('[DEBUG]')

    f_handler = logging.FileHandler('test.log', mode='w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    def star_requests(self):
        for url in self.start_urls:
            yield Request(url,
                          callback=self.parse_response,
                          errback=self.errback_url,
                          dont_filter=True)

    def parse_response(self, response):                 
        selectors = response.xpath('//div[@class=$val]', 
                                val="ListingItem-module__main")
        
        for selector in selectors:
            yield self.parse_item(selector, response)
            
        # Получение ссылки для перехода на след страницу    
        next_sel = response.css('.ListingPagination-module__next::attr(href)')
        
        # Генератор для извлечения следующей страницы
        for next_page in next_sel.extract():
            yield Request(url_parse.urljoin(response.url, next_page),
                          callback=self.parse_response,
                          errback=self.errback_url,
                          dont_filter=True)

    def parse_item(self, selector, response):
        carInfoLoader = CarLoader(item=CarBriefItem(), selector=selector)
        area = self.parse_url(response.url)
        
        if selector.css('.ListingItem-module__kmAge::text').get() == 'Новый':
            carInfoLoader.parse_new(area)
        else:
            carInfoLoader.parse_old(area)
        
        return carInfoLoader.load_item()
    
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
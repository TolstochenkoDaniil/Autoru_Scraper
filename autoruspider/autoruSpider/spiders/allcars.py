from scrapy import Spider
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import urllib.parse as url_parse
import logging
import pandas as pd
import os

from ..items import CarBriefItem, CarLoader

class AllCars(Spider):
    name = "all_cars"
    allowed_domains = ['auto.ru']
    if os.path.exists(r'C:\Users\tolstochenko.d\dev\py\Autoru_Scraper-master\Autoru_Scraper-master\brands.csv'):
        start_urls = list(pd.read_csv(r'C:\Users\tolstochenko.d\dev\py\Autoru_Scraper-master\Autoru_Scraper-master\brands.csv', 
                                  sep = ',',
                                  header=0)
                      .iloc[:,2])
    else:
        start_urls = []
    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'autoru.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8'
        }
    
    logger = logging.getLogger('debug_info')

    f_handler = logging.FileHandler(r'log\autoru.log', mode='w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    def parse (self, response):
        self.logger.info("Response url in `parse` function: %s", response.url)
        
        next_sel = response.css('.ListingPagination-module__next::attr(href)')
        
        # Генератор для извлечения следующей страницы
        for next_page in next_sel.extract():
            yield Request(url_parse.urljoin(response.url, next_page))
            
        selectors = response.xpath('//div[@class=$val]', 
                                val="ListingItem-module__main")
        
        for selector in selectors:
            yield self.parse_item(selector, response)

    def parse_item(self, selector, response):
        carInfoLoader = CarLoader(item=CarBriefItem(), selector=selector)
        self.logger.info("Response url in `parse_item` function: %s",response.url)
        
        if selector.css('.ListingItem-module__kmAge::text').get() == 'Новый':
            carInfoLoader.parse_new()
        else:
            carInfoLoader.parse_old()
        
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
from scrapy import Spider
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import urllib.parse as url_parse
import logging
import pandas as pd

from ..items import CarBriefItem, CarLoader
# should be stored in db?

class AllCars(Spider):
    name = "all_cars"
    allowed_domains = ['auto.ru']
    start_urls = list(pd.read_csv(r'C:\Users\tolstochenko.d\dev\py\Autoru_Scraper-master\Autoru_Scraper-master\autoruSpider\autoruSpider\brands.csv', 
                                  sep = ',',
                                  header=0)
                      .iloc[:,2])
    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'all.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8'
        }
    
    logger = logging.getLogger('debug_info')

    f_handler = logging.FileHandler('all_cars.log')
    f_handler.setLevel(logging.DEBUG)
    f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    def parse (self, response):
        self.logger.info("Initial response %s", repr(response))
        
        for url in self.start_urls:
            self.logger.debug("Current url: %s", url) 
            yield Request(url,
                          callback=self.parse_url,
                          errback=self.errback_url,
                          dont_filter=True)    
    
    def parse_url(self, response):
        self.logger.debug("Response for url %s", response.url)

        selectors = response.xpath('//div[@class=$val]', 
                                val="ListingItem-module__main")
        for selector in selectors:
            yield self.parse_item(selector, response)

    def parse_item(self, selector, response):
        carInfoLoader = CarLoader(item=CarBriefItem(), selector=selector)
        
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
            
            
            
            
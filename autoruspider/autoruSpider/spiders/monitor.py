from scrapy import Spider
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging
import urllib.parse as url_parse
import re
import os
import pandas as pd

from ..items import CarBriefItem, CarLoader

class Monitor(Spider):
    name = 'monitor'
    allowed_domains = ['auto.ru']
    path = os.path.join(os.getcwd(),"csv","brands.csv")
    log = os.path.join(os.getcwd(),"log","monitor.log")
    
    logger = logging.getLogger(__name__)

    f_handler = logging.FileHandler(log, mode='w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)
    
    if os.path.exists(path):
        start_urls = list(pd.read_csv(path, header=0).iloc[:,2])
    else:
        logger.warning("No input file with urls.")
    
    def start_requests(self):
        self.logger.info("Spider {} started crawling.".format(self.name))
        for url in self.start_urls:
            yield Request(url,
                          callback=self.parse,
                          errback=self.errback_url,
                          dont_filter=False)

    def parse(self, response):    
        self.logger.info("Parsing response {}".format(response.url))             
        selectors = response.xpath('//div[@class=$val]', 
                                   val="ListingItem-module__main")
        
        for selector in selectors:
            yield from self.parse_item(selector, response)
            
        # Получение ссылки для перехода на след страницу    
        next_sel = response.css('.ListingPagination-module__next::attr(href)')
        
        # Генератор для извлечения следующей страницы
        for next_page in next_sel.extract():
            yield Request(url_parse.urljoin(response.url, next_page),
                          callback=self.parse,
                          errback=self.errback_url,
                          dont_filter=False)

    def parse_item(self, selector, response):
        carInfoLoader = CarLoader(item=CarBriefItem(), selector=selector)
        area = self.parse_url(response.url)
           
        if selector.css('.ListingItem-module__kmAge::text').get() == 'Новый':
            yield None
        else:
            carInfoLoader.add_value('area', area)
            carInfoLoader.parse_old()
         
            yield carInfoLoader.load_item()
    
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
from scrapy import Spider, signals
from scrapy.http import Request
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.project import get_project_settings
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import re
import os
import json
import logging
from requests import post
import urllib.parse as url_parse

from ..items import CarBriefItem, CarLoader

class Monitor(Spider):
    name = 'monitor'
    allowed_domains = ['auto.ru']
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'autoruSpider.pipelines.DatabasePipeline': 500,
        },
        'SPIDER_MIDDLEWARES':{
            'autoruSpider.middlewares.MonitorSpiderMiddleware':300
        },
        'EXTENSIONS': {
            'autoruSpider.extensions.SetupSpiderLogging': 200,
            'autoruSpider.extensions.TelegramLogger': 300,
        },
    }
    
    start_urls = []
    
    def __init__(self, path=None, *args, **kwargs):
        '''
            Custom init function to pass parameters to spider.\r\n
            @param: `path` where start_urls file located 
            related to project folder(where `settings.py` file is stored).
        '''
        super().__init__(*args,**kwargs)
        self.path = path
        
        if path:
            abspath = os.path.join(get_project_settings().get('BASE_DIR'),path)
            if os.path.exists(abspath):
                
                with open(abspath,'r') as f:
                    data = json.loads(f.read())
                    
                self.start_urls = [url['link'] for url in data]
                self.logger.info("Reading urls from file.")
                self.path = abspath
            else:
                self.logger.warning("Path does not exists")
        else:
            self.logger.info("No input file with urls.")
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        
        return spider
    
    def spider_closed(self, reason):
        payload = {"status": reason}
        
        if not self.path:
            url = get_project_settings().get("APPRAISAL_SERVICE")
        else:
            url = get_project_settings().get("UPDATE_SERVICE")
        try:
            response = post(url=url,json=payload)
        except Exception as error:
            self.logger.error(f"Exception requesting lead service\n{error}")
        else:
            self.logger.info(f"Response from lead service: {response.text}")
       
        
    def spider_opened(self):
        self.logger.info(f"Spider {self.name} opened")
        
    def start_requests(self):
        self.logger.info("Spider {} starts crawling.".format(self.name))
        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError("Spider {} does not have values in 'start_urls'.")
        else:
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
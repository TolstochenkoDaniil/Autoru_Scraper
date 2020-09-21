from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import os

from ..items import RusprofileItem,RusprofileLoader

class Profile(CrawlSpider):
    name = 'profile'
    allowed_domains = ['rusprofile.ru']
    
    custom_settings = {
        'EXTENSIONS': {
            'rusprofile.extensions.SetupSpiderLogging': 200,
        }
    }
    
    start_urls = [
        'https://www.rusprofile.ru/search?query={}&type=ul'
    ]
    
    def __init__(self, inn=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not inn:
            raise AttributeError(
                "Required attribute `inn` is missing\n"
                f"Provide correct input value to spider {self.name}"
            )
        self.inn = [inn]

    @classmethod 
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.item_scraped, signal=signals.item_scraped)
        
        return spider
    
    def spider_opened(self):
        pass
    
    def item_scraped(self, item, response):
        self.logger.info(f"Scraped item:\n{item}")
            
    def start_requests(self):
        
        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError(f"Spider {self.name} does not have values in 'start_urls'")
        else:
            self.start_urls = [url.format(inn) for url, inn in zip(self.start_urls,self.inn)]
        
        for url in self.start_urls:
            yield Request(
                url=url,
                callback=self.parse,
                errback=self.errback_request,
                dont_filter=True
            )
            
    def parse(self, response):
        self.logger.info(f"Response url: {response.url}")

        profile_loader = RusprofileLoader(item=RusprofileItem(), response=response)
        profile_loader.load_profile(response.url)
        
        yield profile_loader.load_item()
        
    def errback_request(self, failure):
        self.logger.error(repr(failure))
        
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error(f"HttpError on {response.url}")
        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error(f"DNSLookupError on {request.url}")
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error(f"TimeoutError on {request.url}")
            
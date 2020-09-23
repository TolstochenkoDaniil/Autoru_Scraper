from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC

import os
import time

from ..items import RusprofileItem, RusprofileLoader

class Profile(CrawlSpider):
    name = 'profile'
    allowed_domains = ['rusprofile.ru']
    
    custom_settings = {
        'EXTENSIONS': {
            'rusprofile.extensions.SetupSpiderLogging': 200,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'rusprofile.middlewares.RusprofileSeleniumMiddleware': 300
        }
    }
    
    start_urls = [
        'https://www.rusprofile.ru/search?query={}&type=ul'
    ]
    
    def __init__(self, inn=None, ogrn=None, new_lead=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not ogrn:
            raise AttributeError(
                "Required attribute `ogrn` is missing\n"
                f"Provide correct input value to spider {self.name}"
            )
            
        self.param = ["+".join((str(ogrn),str(inn))) if inn else str(ogrn)]
        self.new_lead = new_lead

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
            self.start_urls = [url.format(param) for url, param in zip(self.start_urls,self.param)]

        for url in self.start_urls:
            if self.new_lead:
                pdf_button_selector='.btn.btn-white.btn-icon.btn-pdf-icon.gtm_main_pdf'
                yield SeleniumRequest(
                    url=url,
                    callback=self.get_pdf,
                    errback=self.errback_request,
                    dont_filter=True,
                    wait_time=10,
                    wait_until=EC.element_to_be_clickable((
                        By.CSS_SELECTOR,
                        pdf_button_selector
                    )),
                    cb_kwargs=dict(
                        selector=pdf_button_selector
                    )
                )
            else:
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
    
    def get_pdf(self, response, selector):
        self.logger.info(f"Downloading pdf from {response.url}")
        
        driver = response.request.meta.get('driver')
        driver.find_element_by_css_selector(selector).click()
        time.sleep(5)
        driver.close()
        
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
            
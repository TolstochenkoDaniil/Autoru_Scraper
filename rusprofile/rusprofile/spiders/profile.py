from scrapy import signals
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.utils.project import get_project_settings
from scrapy.utils.url import url_is_from_spider
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC

import os
import re
import time
import requests

from ..items import RusprofileItem, RusprofileLoader

class Profile(CrawlSpider):
    name = 'profile'
    allowed_domains = ['rusprofile.ru']
    handle_http_status_list = [301,302,303]
    custom_settings = {
        'EXTENSIONS': {
            'rusprofile.extensions.SetupSpiderLogging': 200,
        },
    }
    
    start_urls = [
        'https://www.rusprofile.ru/search?query={}&type=ul'
    ]
    
    def __init__(self, inn=None, ogrn=None, new_lead=False, OID=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not ogrn and not inn:
            raise AttributeError(
                "Required attribute `ogrn` and `inn` is missing\n"
                f"Provide correct input value to spider {self.name}"
            )
        if not OID:    
            raise AttributeError(
                "Required attribute `OID` is missing\n"
                f"Provide correct input value to spider {self.name}"
            )
        param = []
        self.OID = OID
        if ogrn:
            param.append(str(ogrn))
        if inn:
            param.append(str(inn))
        self.param = "+".join(param)
        self.new_lead = new_lead
        # self.param = ["+".join((str(ogrn),str(inn))) if inn else str(ogrn)]

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
            yield Request(
                url=url,
                callback=self.parse,
                errback=self.errback_request,
                dont_filter=True
            )
            
    def parse(self, response):
        self.logger.info(f"Response url: {response.url}")
        if self.new_lead:
            yield Request(
                    url=response.url+'?print=pdf',
                    callback=self.download_pdf,
                    errback=self.errback_request,
                    dont_filter=True
                )
        else:
            profile_loader = RusprofileLoader(item=RusprofileItem(), response=response)
            profile_loader.load_profile(response.url)
            
            yield profile_loader.load_item()
    
    def download_pdf(self, response):
        raw_cookies = response.headers.getlist('Set-Cookie')[0]
        pdf_link = response.css('iframe::attr(src)').get()
        sessid = re.search('(?<=sessid=).*?(?=;)',raw_cookies.decode('utf-8')).group(0)
        cookies = {
            'sessid':sessid
        }
        yield Request(
            url=pdf_link,
            cookies=cookies,
            callback=self.attach_pdf_to_lead,
            errback=self.errback_request,
            dont_filter=True
        )
        
    def attach_pdf_to_lead(self,response):
        print(f"download pdf from {response.url}")
        
        headers = {
            'Authorization': 'Bearer 030359934E656E42AFC756405F3D5C1B',
        }
        data = {
            'OID':self.OID,
            'Notes':'Loaded from "STR-IT-DEV86"',
            'FileTypeOID':None,
            'EmployeeOID':None
        }
        files = {
            'file':response.body
        }
        url = 'https://b2btest.ma.ru/File/UploadFiles'
        api_response = requests.post(
            url=url,
            headers=headers,
            files=files,
            data=data
        )
        self.logger.info(api_response.status_code)
        return 
            
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
            
    def get_pdf(self, response, selector):
        '''
        DEPRECATED
        Method to extract pdf file using selenium driver
        '''
        self.logger.info(f"Downloading pdf from {response.url}")
        
        driver = response.request.meta.get('driver')
        driver.find_element_by_css_selector(selector).click()
        time.sleep(5)
        driver.close()
        
        # pdf_button_selector='.btn.btn-white.btn-icon.btn-pdf-icon.gtm_main_pdf'
            # yield SeleniumRequest(
            #     url=url,
            #     callback=self.get_pdf,
            #     errback=self.errback_request,
            #     dont_filter=True,
            #     wait_time=10,
            #     wait_until=EC.element_to_be_clickable((
            #         By.CSS_SELECTOR,
            #         pdf_button_selector
            #     )),
            #     cb_kwargs=dict(
            #         selector=pdf_button_selector
            #     )
            # )
            
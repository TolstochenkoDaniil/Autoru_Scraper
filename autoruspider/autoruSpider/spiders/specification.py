from scrapy import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy_selenium import SeleniumRequest

import logging
import os
import json
import socket

from ..items import SpecLoader, SpecItem, ImageItem, ImageLoader, QutoLoader, QutoItem

class SpecificationSpider(CrawlSpider):
    '''
        Spider for crawling cars specifications from auto.ru.

        @param: - url for specific model.\n
        @return: - car specification in database.\n
        @return: - images for specific car(brand,model,generation).
    '''
    name = "specification"
    log = os.path.join(os.getcwd(),'log','specification.log')

    logger = logging.getLogger(__name__)

    f_format = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_handler = logging.FileHandler(log, mode='w')
    f_handler.setLevel(logging.INFO)
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    custom_settings = {
        'ITEM_PIPELINES':{
            'autoruSpider.pipelines.SpecPipeline':None,
            'autoruSpider.pipelines.SpecImagesPipeline':300,
            'scrapy.pipelines.images.ImagesPipeline':None,
        },
        'FEEDS':{
            'csv\\specs.csv':{
                'format':'csv',
                'encoding':'utf8',
                'store_empty':False,
                'fields':[
                    'brand','model','generation','modification','car_type',
                    'volume','power','transmission','engine_type',
                    'fuel','wheel_type','acceleration','consumption',
                    'country','car_class','doors','seats',
                    'safety_rating','rating',
                    'length','width','heigth','wheel_base','clearance','front_wigth','back_width','wheel_size',
                    'trunk_size','tank_volume','equiped','full_weight',
                    'speed_num',
                    'front_suspension','back_suspension','front_brakes','back_brakes',
                    'max_speed','consumption_grade','eco_class','emission',
                    'engine_placement','boost_type','max_power','max_spin',
                    'cylinders','cylinders_num','cylinders_valves','cylinder_size',
                    'compression_ratio','power_type',
                    'url'
                    ]
            }
        },
        'IMAGES_STORE':'img'
    }
    allowed_domains = ['auto.ru',
                       'quto.ru']
    start_urls = []
    rules = (
        Rule(LinkExtractor(allow=('specifications/', ), tags=('a'), attrs=('href',)), callback='parse_spec', follow=True),
        Rule(LinkExtractor(allow=('specifications/[0-9_]+/'), tags=('a'), attrs=('href',), unique=True), callback='parse_spec', follow=True)
    )

    def __init__(self, target=None, OID=None, *args, **kwargs):
        '''
            Custom init function to pass parameters to spider.

            @param: url - start url(s) to begin crawling with.
            @param: OID identifier for selection car entities in database.
        '''
        super().__init__(*args,**kwargs)

        if not OID:
            self.logger.warning("OID parameter is empty. Provide correct value to the spider.")
            self.logger.warning("Files would be saved locally.")
            self.path = None
        else:
            self.OID = OID
            if os.path.exists(self.custom_settings['IMAGES_STORE']):
                self.path = r"{}\{}".format(self.custom_settings['IMAGES_STORE'],
                                            self.OID)
            
        self.start_urls.append(target)
        
        if self.start_urls is None:
            self.logger.warning("No url provided to the spider.")
    
    def start_requests(self):
        cls = self.__class__
        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)")
        else:
            for url in self.start_urls:
                if 'quto.ru' in url:
                    self.logger.info("Making request using selenium driver.")
                    yield SeleniumRequest(url=url, callback=self.parse_img_quto)
                else:
                    yield Request(url, dont_filter=True)
                
    def parse_start_url(self, response):
        '''
            Function to parse page with car images.
        '''
        self.logger.info("Spider {} started crawling.".format(self.name))
        self.logger.info("Start url is {}.".format(response.url))
        
        if ('auto.ru/catalog/cars' in response.url) and ('specification' not in response.url):
            return self.parse_img(response)
            
    def parse_spec(self, response):
        '''
            Callback function to parse response from LinkExtractor requests.
        '''
        self.logger.info("Parsing url {}.".format(response.url))
        
        spec_loader = SpecLoader(item=SpecItem(), response=response)
        spec_loader.parse_spec(url=response.url)
        
        yield spec_loader.load_item()

    def parse_img(self, response):
        '''
            Callback for extracting images from ../specification url.
        '''
        self.logger.info("Parsing specification page {}.".format(response.url))
        
        img_loader = ImageLoader(item=ImageItem(), response=response)
        img_loader.parse_img()
        
        return img_loader.load_item()
    
    def parse_img_quto(self, response):
        '''
            Callback for extracting images from 'quto.ru'.
        '''
        self.logger.info("Parsing quto.ru page {}.".format(response.url))
        
        img_loader = QutoLoader(item=QutoItem(), response=response)
        img_loader.parse_img(url=response.url)
        
        yield img_loader.load_item()
        
    def errback_url(self,failure):
        '''
            Callback for processing errors.
        '''
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
            
    def test_func(self, response):
        print("Test run.")
        print("Response url: {}".format(response.url))
        
        groups = response.css('.list-values.list-values_view_ext.clearfix')
        
        field = groups[0].css('.list-values__value::text')
        if field[3].get() == "гибрид":
            print("Это гибрид")
        else:
            print(field[3].get())
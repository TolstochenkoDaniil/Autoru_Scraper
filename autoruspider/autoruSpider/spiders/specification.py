from scrapy import Spider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging
import os
import json

from ..items import SpecLoader, SpecItem, ImageItem, ImageLoader

class SpecificationSpider(CrawlSpider):
    '''
    Spider for crawling cars specifications from auto.ru.

    @input - url for specific model.\n
    @output - car specification in database.
    @output - images for specific car(brand,model,generation).
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
            'autoruSpider.pipelines.DatabasePipeline':None,
            'autoruSpider.pipelines.SpecImagesPipeline':None,
            'scrapy.pipelines.images.ImagesPipeline': 1
        },
        'FEEDS':{
            'csv\\specs.csv':{
                'format':'csv',
                'encoding':'utf8',
                'store_empty':True,
                'fields':[
                    'brand','model','generation','modification',
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
    allowed_domains = ['auto.ru']
    start_urls = []
    rules = (
        Rule(LinkExtractor(allow=('specifications/', ), tags=('a'), attrs=('href',)), callback='parse_spec', follow=True),
        Rule(LinkExtractor(allow=('specifications/[0-9_]+/'), tags=('a'), attrs=('href',), unique=True), callback='parse_spec', follow=True)
    )

    def __init__(self, target=None, *args, **kwargs):
        '''
        Custom init function to pass parameters to spider.

        @input - start url(s) to begin crawling with.
        '''
        super().__init__(*args,**kwargs)

        self.start_urls.append(target)
        if self.start_urls is None:
            self.logger.warning("No url provided to the spider.")
    
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
        spec_loader.parse_spec()
        spec_loader.add_url(response.url)

        yield spec_loader.load_item()

    def parse_img(self, response):
        '''
        Callback for extracting images from ../specification url.
        '''
        self.logger.info("Parsing specification page {}.".format(response.url))
        
        img_loader = ImageLoader(item=ImageItem(), response=response)
        img_loader.parse_img()
        
        return img_loader.load_item()

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
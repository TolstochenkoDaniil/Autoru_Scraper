from scrapy import Spider
from ..items import ModelsItem, ModelsLoader
from scrapy.utils.project import get_project_settings

import logging
import re
import os

class Brands(Spider):
    name = 'brands'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/htmlsitemap/mark_model_catalog.html']
    area_list = ['moskovskaya_oblast', 'leningradskaya_oblast']
    brands_filter = ['toyota', 'kia', 'ford', 'skoda', 'hyundai', 'mercedes']
    
    custom_settings = {
        'FEEDS' : { 
            'brands.json':{
                'format':'json',
                'encoding':'utf8',
                'store_empty':False,
                'fields':['link'],
                'indent':4,
            },
        }
    }
    
    log_dir = get_project_settings().get('LOG_DIR')
    log = os.path.join(log_dir,'brands.log')
    
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    logger = logging.getLogger(__name__)

    f_handler = logging.FileHandler(log, 'w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    def parse(self, response):
        selectors = response.xpath('/html/body/div[1]/div')
        
        for selector in selectors:
            for area in self.area_list:
                yield self.parse_item(selector, response, area)
    
    def parse_item(self, selector, response, area):        
        
        brand = re.split('/', selector.css('::attr(href)').get())[3]
        
        if brand in self.brands_filter or self.brands_filter is None:
            InfoModelsLoader = ModelsLoader(item = ModelsItem(),
                                            selector=selector)
            InfoModelsLoader.get_model(area)
            self.logger.info("Added link: %s", InfoModelsLoader.get_collected_values('link'))
            
            return InfoModelsLoader.load_item()
            
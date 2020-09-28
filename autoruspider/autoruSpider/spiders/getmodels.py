from requests.api import get
from scrapy import Spider
from ..items import ModelsItem, ModelsLoader
from scrapy.utils.project import get_project_settings

import re
import os

class Brands(Spider):
    name = 'brands'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/htmlsitemap/mark_model_catalog.html']
    area_list = [
        'moskovskaya_oblast',
        'leningradskaya_oblast'
    ]
    brands_filter = [
        'nissan', 
        'audi',
        'volkswagen',
        'bmw',
        "toyota", 
        "kia", 
        "ford", 
        "skoda", 
        "hyundai", 
        "mercedes",
    ]
    dump_dir = os.path.join(get_project_settings().get('BASE_DIR'),'json',f'{name}.json')
    custom_settings = {
        'FEEDS' : { 
            r'autoruSpider\json\brands.json':{
                'format':'json',
                'encoding':'utf8',
                'store_empty':False,
                'fields':['link'],
                'indent':4,
            },
        },
        'EXTENSIONS':{
            'autoruSpider.extensions.SetupSpiderLogging': 200,
        }
    }

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
            
            return InfoModelsLoader.load_item()
            
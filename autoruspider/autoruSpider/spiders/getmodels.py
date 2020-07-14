from scrapy import Spider
from ..items import ModelsItem, ModelsLoader
import logging

import re

class Brands(Spider):
    name = 'brands'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/htmlsitemap/mark_model_catalog.html'] # Сюда пихаем ссылку
    area_list = ['moskovskaya_oblast', 'leningradskaya_oblast']

    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'brands.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        'FEED_EXPORT_FIELDS' : ['brand','model','link']}
    
    logger = logging.getLogger('debug_info')

    f_handler = logging.FileHandler('brands.log', 'w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)

    def parse(self, response):
        selectors = response.xpath('/html/body/div[1]/div') # Тег
        
        for selector in selectors:
            for area in self.area_list:
                yield self.parse_item(selector, response, area)
    
    
    def parse_item(self, selector, response, area):        
        brands_filter = ['toyota', 'kia', 'ford', 'skoda', 'hyundai', 'mercedes']
        brand = re.split('/', selector.css('::attr(href)').get())[3]
        
        if brand in brands_filter:
            InfoModelsLoader = ModelsLoader(item = ModelsItem(),
                                            selector=selector)
            InfoModelsLoader.get_model(area)
            self.logger.info("Added link: %s", InfoModelsLoader.get_collected_values('link'))
            
            return InfoModelsLoader.load_item()
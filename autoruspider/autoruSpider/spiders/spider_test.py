from scrapy import Spider

import logging
import re

from ..items import SpiderTestItem, TestLoader, ModelsLoader, ModelsItem

class TestSpider(Spider):
    name = 'TestSpider'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/htmlsitemap/mark_model_catalog.html'] # Сюда пихаем ссылку
    terr_list = ['moskovskaya_oblast', 'leningradskaya_oblast']
    
    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'test.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        # Набор полей для вывода
        'FEED_EXPORT_FIELDS': ['brand','model','link']}
    
    logger = logging.getLogger('debug_info')

    f_handler = logging.FileHandler('test.log')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)
    
    def parse (self, response):
        
        selectors = response.xpath('/html/body/div[1]/div') # Тег
        for selector in selectors:
            for terr in self.terr_list:
                yield self.parse_item(selector, response, terr)
    
    
    def parse_item(self, selector, response, terr):
        filter_brand = re.split('/', selector.css('::attr(href)').get())[3]
        
        if filter_brand == 'toyota':
            InfoModelsLoader = ModelsLoader(item = ModelsItem(),
                                            selector=selector)
            InfoModelsLoader.get_model(terr)
        
            return InfoModelsLoader.load_item()
        
        
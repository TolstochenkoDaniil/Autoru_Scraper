from scrapy import Spider
from ..items import ModelsItem, ModelsLoader

import re

class Brands(Spider):
    name = 'brands'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/htmlsitemap/mark_model_catalog.html']

    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'brands.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        'FEED_EXPORT_FIELDS' : ['brand','model','link']}
    
    def parse(self, response):

        selectors = response.xpath('/html/body/div[1]/div')
        for selector in selectors:
            yield self.parse_item(selector, response)
    
    
    def parse_item(self, selector,response):

        TerrSet = ['moskovskaya_oblast', 'leningradskaya_oblast']
        filter_brand = re.split('/', selector.css('::attr(href)').get())[3]
        
        if filter_brand == 'toyota':
            for terr in TerrSet:
                InfoModelsLoader = ModelsLoader(item = ModelsItem(), selector=selector)
                InfoModelsLoader.get_model()
                
                return InfoModelsLoader.load_item()
                
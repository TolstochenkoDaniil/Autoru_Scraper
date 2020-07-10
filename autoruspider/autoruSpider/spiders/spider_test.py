from scrapy import Spider

import re

from ..items import SpiderTestItem, TestLoader, ModelsLoader, ModelsItem

class TestSpider(Spider):
    name = 'TestSpider'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/htmlsitemap/mark_model_catalog.html'] # Сюда пихаем ссылку

    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'test.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        # Набор полей для вывода
        'FEED_EXPORT_FIELDS': ['ID','title','price','offer_price','year','distance',
                      'engine_type','fuel_type','horse_power',
                      'car_type','wheel_type','transmission',
                      'color','city','advert','link']}
    
    def parse (self, response):

        selectors = response.xpath('/html/body/div[1]/div') # Тег
        for selector in selectors:
            yield self.parse_item(selector, response)
    
    
    def parse_item(self, selector, response):

        TerrSet = ['moskovskaya_oblast', 'leningradskaya_oblast']
        filter_brand = re.split('/', selector.css('::attr(href)').get())[3]
        
        if filter_brand == 'toyota':
            for terr in TerrSet:
                InfoModelsLoader = ModelsLoader(item = ModelsItem(terr), selector=selector)
                InfoModelsLoader.get_model()
                InfoModelsLoader.load_item()
        # comment
        # comment
         # comment
        # comment
         # comment
        # comment
        return None
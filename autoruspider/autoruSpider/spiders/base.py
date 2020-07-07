from scrapy.spiders import Spider
from scrapy.loader import ItemLoader
from scrapy.http import Request
from scrapy.loader.processors import TakeFirst
import logging

from ..items import CarBriefItem, CarLoader

import urllib.parse as url_parse

logger = logging.getLogger('debug_info')

class CarSpider(Spider):
    name = 'toyota'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/moskva/cars/toyota/all/?from=searchline&output_type=list']

    def parse(self, response):
        next_sel = response.css('.ListingPagination-module__next::attr(href)')
        
        # Генератор для извлечения следующей страницы
        for url in next_sel.extract():
            logger.info(url)
            yield Request(url_parse.urljoin(response.url, url))
        
        selectors = response.xpath('//div[@class=$val]', 
                                   val="ListingItem-module__main")
        
        for selector in selectors:
            yield self.parse_item(selector, response)
            
            
    def parse_item(self, selector, response):
        carInfoLoader = CarLoader(item=CarBriefItem(), selector=selector)
        
        if selector.css('.ListingItem-module__kmAge::text').get() == 'Новый':
            #logger.info('New')
            carInfoLoader.parse_new()
        else:
            #logger.info('Old')
            carInfoLoader.parse_old()
        
        return carInfoLoader.load_item()
    
class CamrySpider(CarSpider):
    name = 'camry'
    start_urls = ['https://auto.ru/moskva/cars/toyota/camry/all/?sort=year-asc']
    
    custom_settings = {
        'FEED_URI': 'camry.csv',
    }
    
class CorollaSpider(CarSpider):
    name = 'corolla'
    start_urls = ['https://auto.ru/moskva/cars/toyota/corolla/all/?sort=price-asc']
    
    custom_settings = {
        'FEED_URI': 'corolla.csv',
    }

class AurisSpider(CarSpider):
    name = 'auris'
    start_urls = ['https://auto.ru/moskva/cars/toyota/auris/all/']
    custom_settings = {
        'FEED_URI': 'auris.csv',
    }
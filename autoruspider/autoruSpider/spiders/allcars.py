from scrapy import Spider
from scrapy.http import Request

import urllib.parse as url_parse
import logging
import pandas as pd

class AllCars(Spider):
    name = "all_cars"
    allowed_domains = ['auto.ru']
    urls = pd.read_csv(r'D:\\Python\Autoru_Scraper-master\autoruSpider\autoruSpider\brands.csv', sep = ',').iloc[:,2]
    def __init__(self, *args, **kwargs):
        logger = logging.getLogger('DEBUG')

        f_handler = logging.FileHandler('all_cars.log')
        f_handler.setLevel(logging.DEBUG)
        f_format = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        f_handler.setFormatter(f_format)

        logger.addHandler(f_handler)
        super().__init__(*args, **kwargs)

    def parse (self, response):
        
        for url in self.urls:
            self.logger.debug(url) 
            self.logger.debug("Response structure {0}".format(response))
            Request(url_parse.urljoin(response.url, url))
            self.logger.debug("Response from url request {0}".format(response))

            selectors = response.xpath('//div[@class=$val]', 
                                    val="ListingItem-module__main")

            for selector in selectors:
                yield self.parse_item(selector, response)    
    
    def parse_item(self, selector, response):
        carInfoLoader = CarLoader(item=CarBriefItem(), selector=selector)
        
        if selector.css('.ListingItem-module__kmAge::text').get() == 'Новый':
            carInfoLoader.parse_new()
        else:
            carInfoLoader.parse_old()
        
        return carInfoLoader.load_item()
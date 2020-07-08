from scrapy import Spider
from ..items import SpiderTestItem, TestLoader

class TestSpider(Spider):
    name = 'TestSpider'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/cars/toyota/all/'] # Сюда пихаем ссылку

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

        selectors = response.xpath('//div[@class=$val]', 
                                   val="ListingItem-module__main") # Тег
        for selector in selectors:
            yield self.parse_ithem(selector, response)
    
    
    def parse_ithem(self, selector,response):

        InfoTestLoader = TestLoader(item = SpiderTestItem(), selector=selector)
        InfoTestLoader.get_test_fields()

        return InfoTestLoader.load_item()
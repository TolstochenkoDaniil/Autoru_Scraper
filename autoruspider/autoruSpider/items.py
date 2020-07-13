# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, Identity, Compose, TakeFirst

import urllib.parse as url_parse
import re
#import datetime
    
# def raw_field():
#     def parse_raw_line(value):
#         pattern = re.compile('\s./|\s.\..\./')
#         attr_list = pattern.split(value)
#         return attr_list
        
#     return scrapy.Field(
#         input_processor=MapCompose(lambda value: value.replace(u'\u2009', u''),
#                                    lambda value: value.replace(u'\xa0', u' '),
#                                    parse_raw_line)
#     )

class CarBriefItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(lambda value: value.replace(u'\xa0', u''),
                                   lambda value: value.replace('\u20bd', u'')),
    )
    year = scrapy.Field()
    distance = scrapy.Field(
        input_processor=MapCompose(lambda value: value.replace(u'\xa0', u''),
                                   lambda value: value.replace(u'км', u''))
    )

    # raw_data = raw_field()
    # engine_type = scrapy.Field(
    #     output_processor=Compose(lambda value: value[0])
    # )
    # horse_power = scrapy.Field(
    #     output_processor=Compose(lambda value: value[1])
    # )
    # fuel_type = scrapy.Field(
    #     output_processor=Compose(lambda value: value[2])
    # )

    engine_type = scrapy.Field(
        output_processor=MapCompose(lambda value: re.split('/', value)[0],
                                    lambda value: value.replace('л','').strip()) # text: 1.6 л / 105 л.с. / Бензин
    )
    horse_power = scrapy.Field(
        output_processor=MapCompose(lambda value: re.split('/', value)[1],
                                    lambda value: value.replace('л.с.','').strip())
    )
    fuel_type = scrapy.Field(
        output_processor=MapCompose(lambda value: re.split('/', value)[2].strip())
    )
    transmission = scrapy.Field()
    car_type = scrapy.Field()
    wheel_type = scrapy.Field()
    color = scrapy.Field()
    city = scrapy.Field()
    advert = scrapy.Field()
    link = scrapy.Field()
    time_stamp = scrapy.Field()
    offer_price = scrapy.Field()
    ID = scrapy.Field(
        output_processor=MapCompose(lambda value: url_parse.urlparse(value).path,
                                    lambda value: re.findall('[0-9]+\-.*[^/]',value)
                                    )
    )
    IsMSK = scrapy.Field()

class CarLoader(ItemLoader):
    default_output_processor = TakeFirst()
    
    def parse_old(self):
        self.add_xpath('title', 
                           './/h3[@class="ListingItemTitle-module__container ListingItem-module__title"]//text()')
        self.add_xpath('engine_type', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('horse_power', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('fuel_type', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')

        self.add_xpath('transmission', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][2]//text()')
        self.add_xpath('car_type', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][3]//text()')
        self.add_xpath('wheel_type', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][2]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('color', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][2]/div[@class="ListingItemTechSummaryDesktop__cell"][2]//text()')
        self.add_xpath('price', 
                           './/div[@class="ListingItemPrice-module__content"]//text()')
        self.add_xpath('city', 
                           './/span[@class="MetroListPlace__regionName MetroListPlace_nbsp"]//text()')
        self.add_xpath('year', 
                           './/div[@class="ListingItem-module__year"]//text()')
        self.add_xpath('distance', 
                           './/div[@class="ListingItem-module__kmAge"]//text()')
        try:
            self.add_css('advert', 
                         '.Link.ListingItemSalonName-module__container.ListingItem-module__salonName::text')
        except:
            self.add_value('advert', 'owner')
        self.add_css('link','.Link.ListingItemTitle-module__link::attr(href)')
        self.add_css('offer_price','.OfferPriceBadge::text')
        self.add_css('ID','.Link.ListingItemTitle-module__link::attr(href)')
    
    def parse_new(self):
        self.add_xpath('title', 
                           './/h3[@class="ListingItemTitle-module__container ListingItem-module__title"]//text()')

        # self.add_xpath('raw_data', 
        #                    './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        # self.add_value('engine_type', 
        #                         self.get_collected_values('raw_data'))
        # self.add_value('horse_power', 
        #                         self.get_collected_values('raw_data'))
        # self.add_value('fuel_type', 
        #                         self.get_collected_values('raw_data'))

        self.add_xpath('engine_type', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('horse_power', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('fuel_type', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()') 
                              
        self.add_xpath('car_type', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][2]//text()')
        self.add_value('color', 'NaN')
        self.add_xpath('wheel_type', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][2]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('transmission', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][2]/div[@class="ListingItemTechSummaryDesktop__cell"][2]//text()')
        self.add_xpath('price', 
                           './/div[@class="ListingItemPrice-module__content"]//text()')
        self.add_xpath('city', 
                           './/span[@class="MetroListPlace__regionName MetroListPlace_nbsp"]//text()')
        self.add_xpath('year', 
                           './/div[@class="ListingItem-module__year"]//text()')
        self.add_value('distance', 'NaN')
        self.add_css('advert', 
                       '.Link.ListingItemSalonName-module__container.ListingItem-module__salonName::text')
        self.add_css('link','.Link.ListingItemTitle-module__link::attr(href)')
        self.add_css('offer_price','.OfferPriceBadge::text')
        self.add_css('ID','.Link.ListingItemTitle-module__link::attr(href)')

class ModelsItem(scrapy.Item):
    #Рабочая версия получения параметров из строк
    
    brand = scrapy.Field(
            output_processor=MapCompose(lambda value: re.split('/',value)[3])
        )
    model = scrapy.Field(
            output_processor=MapCompose(lambda value: re.split('/',value)[4])
        )
    link = scrapy.Field(
            output_processor=MapCompose(lambda value: ''.join(['https://auto.ru/',
                                                              value.get('terr'),
                                                              value.get('url').replace('/catalog',''),
                                                              'all/']))
        )

class ModelsLoader(ItemLoader):
    default_output_processor = TakeFirst()
    
    def get_model(self, terr):
        params = {}
        params['terr'] = terr
        params['url'] = self.get_css('::attr(href)')[0]
        self.add_value('link', params)
        self.add_css('brand','::attr(href)')
        self.add_css('model','::attr(href)')
        
# Test
#_________________________________________________________#
class SpiderTestItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(lambda value: value.replace(u'\xa0', u''),
                                   lambda value: value.replace('\u20bd', u'')),
    )
    year = scrapy.Field()
    distance = scrapy.Field(
        input_processor=MapCompose(lambda value: value.replace(u'\xa0', u''),
                                   lambda value: value.replace(u'км', u''))
    )

    engine_type = scrapy.Field(
        output_processor=MapCompose(lambda value: re.split('/', value)[0],
                                    lambda value: value.replace('л','').strip()) # text: 1.6 л / 105 л.с. / Бензин
    )
    horse_power = scrapy.Field(
        output_processor=MapCompose(lambda value: re.split('/', value)[1],
                                    lambda value: value.replace('л.с.','').strip())
    )
    fuel_type = scrapy.Field(
        output_processor=MapCompose(lambda value: re.split('/', value)[2].strip())
    )
    transmission = scrapy.Field()
    car_type = scrapy.Field()
    wheel_type = scrapy.Field()
    color = scrapy.Field()
    city = scrapy.Field()
    advert = scrapy.Field()
    link = scrapy.Field()
    time_stamp = scrapy.Field()
    offer_price = scrapy.Field()
    ID = scrapy.Field(
        output_processor=MapCompose(lambda value: url_parse.urlparse(value).path,
                                    lambda value: re.findall('[0-9]+\-.*[^/]',value)
                                )
    )

class TestLoader(ItemLoader):
    default_output_processor = TakeFirst()

    def get_test_fields(self):
        self.add_xpath('title', 
                           './/h3[@class="ListingItemTitle-module__container ListingItem-module__title"]//text()')
        
        self.add_xpath('engine_type', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('horse_power', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('fuel_type', 
                            './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('car_type', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][1]/div[@class="ListingItemTechSummaryDesktop__cell"][2]//text()')
        self.add_value('color', 'NaN')
        self.add_xpath('wheel_type', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][2]/div[@class="ListingItemTechSummaryDesktop__cell"][1]//text()')
        self.add_xpath('transmission', 
                           './/div[@class="ListingItemTechSummaryDesktop__column"][2]/div[@class="ListingItemTechSummaryDesktop__cell"][2]//text()')
        self.add_xpath('price', 
                           './/div[@class="ListingItemPrice-module__content"]//text()')
        self.add_xpath('city', 
                           './/span[@class="MetroListPlace__regionName MetroListPlace_nbsp"]//text()')
        self.add_xpath('year', 
                           './/div[@class="ListingItem-module__year"]//text()')
        self.add_value('distance', 'NaN')
        self.add_css('advert', 
                       '.Link.ListingItemSalonName-module__container.ListingItem-module__salonName::text')
        self.add_css('link','.Link.ListingItemTitle-module__link::attr(href)')
        self.add_css('offer_price','.OfferPriceBadge::text')
        self.add_css('ID','.Link.ListingItemTitle-module__link::attr(href)')
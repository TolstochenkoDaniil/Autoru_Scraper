import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, Identity, Compose, TakeFirst

import urllib.parse as url_parse
import re
import datetime
    
def serializer_int(value):
    if isinstance(value,list) and value:
        value = value.pop()
    return int(value)
    
def serializer_float(value):
    if isinstance(value,list):
        value = value.pop()
    return float(value)

def serialize_area(value):
    area = {"moskovskaya_oblast":"Москва",
            "leningradskaya_oblast":"Санкт-Петербург"}
    value = area[value]
    
    return value
    
class CarBriefItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace(u'\xa0', u''),
                                lambda value: value.replace('\u20bd', u''),
                                lambda value: value.replace(u'от ', u'')),
        output_processor=serializer_int
    )
    year = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                serializer_int)
        )
    distance = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace(u'\xa0', u''),
                                lambda value: value.replace(u'км', u'')),
        output_processor=serializer_int
    )
    engine_type = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.split('/')[0],
                                lambda value: value.replace('л','').strip()), # text: 1.6 л / 105 л.с. / Бензин
        output_processor=serializer_float
    )
    horse_power = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.split('/')[1],
                                lambda value: value.replace('л.с.','').strip()),
        output_processor=serializer_int
    )
    fuel_type = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.split('/')[2].strip())
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
        input_processor=Compose(TakeFirst(),
                                lambda value: url_parse.urlparse(value).path,
                                lambda value: re.findall('[0-9]+\-.*[^/]',value))
    )
    area = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                serialize_area)
    )
    date = scrapy.Field()

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
        self.add_xpath('city', 
                       './/span[@class="MetroListPlace__regionName MetroListPlace_nbsp"]//text()')
        self.add_xpath('year', 
                       './/div[@class="ListingItem-module__year"]//text()')
        self.add_xpath('distance', 
                       './/div[@class="ListingItem-module__kmAge"]//text()')
        self.add_css('link','.Link.ListingItemTitle-module__link::attr(href)')
        self.add_css('offer_price','.OfferPriceBadge::text')
        self.add_css('ID','.Link.ListingItemTitle-module__link::attr(href)')
        self.add_value('date', datetime.date.today().isoformat())
        self.add_css('advert',
                     '.Link.ListingItemSalonName-module__container.ListingItem-module__salonName::text')
        
        if not self.get_collected_values('advert'):
            self.add_value('advert','owner')
                    
        self.add_xpath('price', 
                       './/div[@class="ListingItemPrice-module__content"]//text()')
        
        if not self.get_collected_values('price'):
            self.replace_value('price', '0')
            
    def parse_new(self):
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
        self.add_xpath('city', 
                       './/span[@class="MetroListPlace__regionName MetroListPlace_nbsp"]//text()')
        self.add_xpath('year', 
                       './/div[@class="ListingItem-module__year"]//text()')
        self.add_value('distance', '0')
        self.add_css('link','.Link.ListingItemTitle-module__link::attr(href)')
        self.add_css('offer_price','.OfferPriceBadge::text')
        self.add_css('ID','.Link.ListingItemTitle-module__link::attr(href)')
        self.add_value('date', datetime.date.today().isoformat())
        self.add_css('advert', 
                     '.Link.ListingItemSalonName-module__container.ListingItem-module__salonName::text')
        self.add_xpath('price', 
                       './/div[@class="ListingItemPrice-module__content"]//text()')
        
        if not self.get_collected_values('price'):
            self.replace_value('price', '0')
            
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

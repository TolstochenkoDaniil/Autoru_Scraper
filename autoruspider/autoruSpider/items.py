import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, Identity, Compose, TakeFirst

import urllib.parse as url_parse
import re
import datetime
import json
    
def serializer_int(value):
    if isinstance(value,list) and value:
        value = value.pop()
    try:
        return int(value)
    except:
        return value
    
def serializer_float(value):
    if isinstance(value,list):
        value = value.pop()
    try:
        return float(value)
    except:
        return value

def serialize_area(value):
    area = {"moskovskaya_oblast":"Москва",
            "leningradskaya_oblast":"Санкт-Петербург"}
    value = area[value]
    
    return value

##############################
### Monitor Spider section ###
##############################
    
class CarBriefItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: re.sub('\s+',' ',value))
    )
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

############################
### Brand Spider section ###
############################ 
         
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
        
####################################
### Specification Spider section ###
####################################

class SpecItem(scrapy.Item):
    '''
        Item model for `specification` spider.
        Matches car specification from auto.ru/../specifications
    '''
    # car credentials
    modification = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.replace('Модификация ', ''))
    )
    brand = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.lower().rstrip())
    )
    model = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.lower().rstrip())
    )
    generation = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.lower().rstrip())
    )
    car_type = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.lower().rstrip())
    )
    
    # modification options
    volume = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace('л','').strip()),
        output_processor=serializer_float
    )
    fuel = scrapy.Field()
    power = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace('л.с.','').strip()),
        output_processor=serializer_int
    )
    wheel_type = scrapy.Field()
    transmission = scrapy.Field()
    acceleration = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace('с','').strip()),
        output_processor=serializer_float
    )
    engine_type = scrapy.Field()
    consumption = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace('л','').strip()),
        output_processor=serializer_float
    )
    
    # common info
    country = scrapy.Field()
    car_class = scrapy.Field()
    doors = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    seats = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    
    """ 
    Deprecated group.
    
    # safety
    safety_rating = scrapy.Field()
    rating = scrapy.Field()
     """
     
    # size
    length = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    width = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    heigth = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    wheel_base = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    clearance = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    front_width = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    back_width = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    wheel_size = scrapy.Field()
    
    # volume and weight
    trunk_volume = scrapy.Field()
    tank_volume = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    equiped = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    full_weight = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )

    # transmission
    speed_num = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    
    # suspension and brakes
    front_suspension = scrapy.Field()
    back_suspension = scrapy.Field()
    front_brakes = scrapy.Field()
    back_brakes = scrapy.Field()
    
    # performance indicators
    max_speed = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    consumption_grade = scrapy.Field()
    eco_class = scrapy.Field()
    emissions = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
            
    # engine
    engine_placement = scrapy.Field()
    engine_volume = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_float
    )
    boost_type = scrapy.Field()
    max_power = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace('\u2009',' ').strip())
    )
    max_spin = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda value: value.replace('\u2009',' ').strip())
    )
    cylinders = scrapy.Field()
    cylinders_num = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    cylinders_valves = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_int
    )
    power_type = scrapy.Field()
    compression_ratio = scrapy.Field(
        input_processor=TakeFirst(),
        output_processor=serializer_float
    )
    cylinder_size = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.replace('\xd7', 'x'))
    )  
    
    # miscellaneous
    url = scrapy.Field()

class SpecLoader(ItemLoader):
    '''
        Loader for `SpecItem()` object.
    '''
    default_output_processor = TakeFirst()
    
    option_dict = {
            'Объем':'volume',
            'Мощность':'power',
            'Коробка':'transmission',
            'Тип двигателя':'engine_type',
            'Топливо':'fuel',
            'Привод':'wheel_type',
            'Разгон':'acceleration',
            'Расход':'consumption',
            'Страна марки':'country',
            'Класс автомобиля':'car_class',
            'Количество дверей':'doors',
            'Количество мест':'seats',
            'Длина':'length',
            'Ширина':'width',
            'Высота':'heigth',
            'Колёсная база':'wheel_base',
            'Клиренс':'clearance',
            'Размер колёс':'wheel_size',
            'Ширина передней колеи':'front_width',
            'Ширина задней колеи':'back_width',
            'Объем багажника мин/макс, л':'trunk_volume',
            'Объём топливного бака, л':'tank_volume',
            'Снаряженная масса, кг':'equiped',
            'Полная масса, кг':'full_weight',
            'Количество передач':'speed_num',
            'Тип передней подвески':'front_suspension',
            'Тип задней подвески':'back_suspension',
            'Передние тормоза':'front_brakes',
            'Задние тормоза':'back_brakes',
            'Выбросы CO2, г/км':'emissions',
            'Максимальная скорость, км/ч':'max_speed',
            'Расход топлива, л город/трасса/смешанный':'consumption_grade',
            'Экологический класс':'eco_class',
            'Расположение двигателя':'engine_placement',
            'Объем двигателя, см³':'engine_volume',
            'Тип наддува':'boost_type',
            'Максимальная мощность, л.с./кВт при об/мин':'max_power',
            'Максимальный крутящий момент, Н*м при об/мин':'max_spin',
            'Расположение цилиндров':'cylinders',
            'Количество цилиндров':'cylinders_num',
            'Число клапанов на цилиндр':'cylinders_valves',
            'Система питания двигателя':'power_type',
            'Степень сжатия':'compression_ratio',
            'Диаметр цилиндра и ход поршня, мм':'cylinder_size'
        }
    
    def parse_spec(self,url=None):  
        '''
            Method for parsing specification page content.
        '''      
        # car credentials
        self.add_css('modification',".catalog__header::text")
        self.add_css('brand','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_mark.link__control.i-bem::text')
        self.add_css('model','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_model.link__control.i-bem::text')
        self.add_css('generation','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_generation.link__control.i-bem::text')
        self.add_css('car_type','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_configuration.link__control.i-bem::text')
        
        content = self.selector.css('.catalog__content')
        
        # options and values are paired
        options = [option.css('.list-values__value::text').get(default='empty') for option in content.css('.list-values__value')]
        labels = [label.css('.list-values__label::text').get(default='empty') for label in content.css('.list-values__label')]
        
        for label,option in zip(labels,options):
            if self.option_dict.get(label,None):
                self.add_value(self.option_dict[label],option)

        if url:
            self.add_value('url', url)
        
class ImageItem(scrapy.Item):
    '''
        Item class for storing images with car credentials.
    '''
    _brand = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.lower().rstrip())
    )
    _model = scrapy.Field(
        input_processor=Compose(TakeFirst(),
                                lambda x: x.lower().rstrip())
    )
    _generation = scrapy.Field()
    _car_type = scrapy.Field()
    
    image_urls = scrapy.Field(
        output_processor = Identity()
    )
    image = scrapy.Field()
    
class ImageLoader(ItemLoader):
    '''
        Loader for `ImageItem()` object parsed from 'auto.ru'.
    '''
    default_output_processor = TakeFirst()
    
    def parse_img(self):
        '''
            Function for extracting images from auto.ru/../specification url.
        '''
        # add image urls as json
        img = json.loads(str(self.selector.css('.photo-gallery.model-gallery.i-bem::attr(data-bem)').get()))
        img_urls = list(''.join(('https:',url['img'])) for url in img['photo-gallery']['photos'])
        self.add_value('image_urls',img_urls)
        # add credentials
        self.add_css('_brand','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_mark.link__control.i-bem::text')
        self.add_css('_model','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_model.link__control.i-bem::text')
        self.add_css('_generation','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_generation.link__control.i-bem::text')
        _car_type = json.loads(self.selector.css('.sale-data-attributes.sale-data-attributes_hidden.i-bem::attr(data-bem)').getall().pop())
        self.add_value('_car_type',_car_type['sale-data-attributes']['type'])
        
class QutoItem(ImageItem):
    '''
        Item class for storing images specific for quto.ru domain.
    '''
    image_urls = scrapy.Field(
        input_processor=MapCompose(
            lambda x: re.search('(?<=\(\)).*', x).group(0),
            lambda x: ''.join(('https://quto.ru',x))
        ),
        output_processor=Identity()
    )
    # f means restyling in quto.ru
    _generation = scrapy.Field(
        input_processor = lambda x: x.replace('f','_restyling') if 'f' in x else x
    )
    # match car type until numbers
    # ex: in str `hatchback5d` will match `hatchback`
    _car_type = scrapy.Field(
        input_processor = MapCompose(
            lambda x: re.match('\w+(?=\d)',x).group(0)
        )
    )
      
class QutoLoader(ItemLoader):
    '''
        Loader for QutoItem() object parsed from 'quto.ru'.
    '''
    default_output_processor = TakeFirst()
    
    def parse_img(self, url=None):
        # src is list of raw img links: 
        # ex: '/thumb/100x0/filters:quality(75):no_upscale()/service-imgs/5e/06/0e/0d/5e060e0d955e6.jpeg'
        src = self.selector.xpath('//img[contains(@class, "_3vBDgiAMbzDhS6NM4MnM3G")]/@src').getall()
        self.add_value('image_urls', src)

        if url:
            url = url_parse.urlparse(url).path.split('/') # ['', 'audi', 'rs7', 'if', 'hatchback5d']
            self.add_value('_brand', url[1])
            self.add_value('_model', url[2])
            self.add_value('_generation', url[3])
            self.add_value('_car_type', url[4])
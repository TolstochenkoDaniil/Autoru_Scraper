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

class SpecItem(scrapy.Item):
    '''
    Item model for specification spider.
    Matches car specification from auto.ru/../specifications
    '''
    # car credentials
    modification = scrapy.Field()
    brand = scrapy.Field()
    model = scrapy.Field()
    generation = scrapy.Field()
    
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
    seats = scrapy.Field()
    
    # safety
    safety_rating = scrapy.Field()
    rating = scrapy.Field()
    
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
        output_processor=serializer_int
    )
    boost_type = scrapy.Field()
    max_power = scrapy.Field()
    max_spin = scrapy.Field()
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
    cylinder_size = scrapy.Field()  
    
    # miscellaneous
    url = scrapy.Field()

class SpecLoader(ItemLoader):
    '''
    Loader for SpecItem() object.
    '''
    default_output_processor = TakeFirst()
    
    def parse_spec(self):
        '''
        Function for parsing specification page on auto.ru
        
        All fields divide in 9 groups.
        2 groups in the footer, 5 in the left table, 2 in the right.
        '''
        # car credentials
        self.add_css('modification',".catalog__header::text")
        self.add_css('brand','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_mark.link__control.i-bem.link_js_inited::text')
        self.add_value('model','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_model.link__control.i-bem.link_js_inited::text')
        self.add_value('generation','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_generation.link__control.i-bem.link_js_inited::text')
        
        mod_groups = self.selector.css('.list-values.list-values_view_ext.clearfix')
        # parse left options table
        l_options = mod_groups[0].css('.list-values__value::text')
        self.add_value('volume', l_options[0].get())
        self.add_value('power', l_options[1].get())
        self.add_value('transmission', l_options[2].get())
        self.add_value('engine_type', l_options[3].get())
        
        # parse right options table
        r_options = mod_groups[1].css('.list-values__value::text')
        self.add_value('fuel', r_options[0].get())
        self.add_value('wheel_type', r_options[1].get())
        self.add_value('acceleration', r_options[2].get())
        self.add_value('consumption', r_options[3].get())

        # parse left table
        groups = self.selector.css('.catalog__details-group')
        
        # common info
        cm_options = groups[0].css('.list-values__value::text')
        self.add_value('country', cm_options[0].get())
        self.add_value('car_class', cm_options[1].get())
        self.add_value('doors', cm_options[2].get())
        self.add_value('seats', cm_options[3].get())
        
        # safety
        sa_options = groups[1].css('.list-values__value::text')
        self.add_value('safety_rating', sa_options[0].get())
        self.add_value('rating', sa_options[1].get())
        
        # size
        sz_options = groups[2].css('.list-values__value::text')
        self.add_value('length', sz_options[0].get())
        self.add_value('width', sz_options[1].get())
        self.add_value('heigth', sz_options[2].get())
        self.add_value('wheel_base', sz_options[3].get())
        self.add_value('clearance', sz_options[4].get())
        self.add_value('front_width',sz_options[5].get())
        self.add_value('back_width',sz_options[6].get())
        self.add_value('wheel_size', sz_options[7].get())
        
        # volume & weight
        vw_options = groups[3].css('.list-values__value::text')
        self.add_value('trunk_volume', vw_options[0].get())
        self.add_value('tank_volume', vw_options[1].get())
        self.add_value('equiped', vw_options[2].get())
        self.add_value('full_weight', vw_options[3].get())
        
        # transmission
        tr_options = groups[4].css('.list-values__value::text')
        self.add_value('speed_num', tr_options[1].get())
        
        # suspension & brakes
        sb_options = groups[5].css('.list-values__value::text')
        self.add_value('front_suspension', sb_options[0].get())
        self.add_value('back_suspension', sb_options[1].get())
        self.add_value('front_brakes', sb_options[2].get())
        self.add_value('back_brakes', sb_options[3].get())
        
        # parse right table
        # performance indicators
        pi_options = groups[6].css('.list-values__value::text')
        self.add_value('max_speed', pi_options[0].get())
        self.add_value('consumption_grade', pi_options[2].get())
        self.add_value('eco_class', pi_options[4].get())
        self.add_value('emissions', pi_options[5].get())
        
        # engine
        en_options = groups[7].css('.list-values__value::text')
        self.add_value('engine_placement', en_options[1].get())
        self.add_value('engine_volume', en_options[2].get())
        self.add_value('boost_type', en_options[3].get())
        self.add_value('max_power', en_options[4].get())
        self.add_value('max_spin', en_options[5].get())
        self.add_value('cylinders', en_options[6].get())
        self.add_value('cylinders_num', en_options[7].get())
        self.add_value('cylinders_valves', en_options[8].get())
        
        # disel cars do not have 'power_type'
        if self.get_collected_values('fuel')[0] != "ДТ":
            self.add_value('power_type', en_options[9].get())
            self.add_value('compression_ratio', en_options[10].get())
            self.add_value('cylinder_size', en_options[11].get())
        else:
            self.add_value('power_type', '-')
            self.add_value('compression_ratio', en_options[9].get())
            self.add_value('cylinder_size', en_options[10].get())
    
    def add_url(self, url):
        self.add_value('url', url)
        
class ImageItem(scrapy.Item):
    '''
    Item class for storing images with car credentials.
    '''
    _brand = scrapy.Field()
    _model = scrapy.Field()
    _generation = scrapy.Field()
    
    image_urls = scrapy.Field()
    image = scrapy.Field()
    
class ImageLoader(ItemLoader):
    '''
    Loader for ImageItem() object.
    '''
    # default_output_processor = TakeFirst()
    
    def parse_img(self):
        '''
        Function for extracting images for auto.ru/../specification url.
        '''
        # add image urlsas json
        img = json.loads(str(self.selector.css('.photo-gallery.model-gallery.i-bem::attr(data-bem)').get()))
        img_urls = list(''.join(('https:',url['thumb'])) for url in img['photo-gallery']['photos'])
        self.add_value('image_urls',img_urls)
        
        # add credentials
        self.add_css('_brand','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_mark.link__control.i-bem.link_js_inited::text')
        self.add_css('_model','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_model.link__control.i-bem.link_js_inited::text')
        self.add_css('_generation','.link.link_pseudo.search-form-v2-mmm__breadcrumbs-item.search-form-v2-mmm__breadcrumbs-item_state_selected.search-form-v2-mmm__breadcrumbs-item_type_generation.link__control.i-bem.link_js_inited::text')
        
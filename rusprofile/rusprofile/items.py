# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose

import re

def serializer_int(value):
    try:
        return int(value)
    except:
        return value

def head_inn(record_list):
    for row in record_list:
        match = re.search("(?<=\()(.{3}\s[0-9]+)(?=\))",row)
        if match:
            inn = re.search("[0-9]+",match)[0]
            if inn:
                return inn
        else:
            return "-"
        
class RusprofileItem(Item):
    name = Field()
    inn = Field()
    kpp = Field()
    ogrn = Field()
    reg_date = Field()
    address = Field()
    head = Field()
    head_inn = Field(
        input_processor=head_inn
    )
    capital = Field(
        input_processor=Compose(
            TakeFirst(),
            lambda x: x.replace(" руб.","").replace(" ",""),
            lambda x: int(x)
        )
    )
    activity = Field(
        input_processor=Compose(
            TakeFirst(),
            lambda x: x.strip()
        )
    )
    activity_code = Field(
        input_processor=Compose(
            TakeFirst(),
            lambda x: re.search('(?<=\().*?(?=\))',x)[0]
        )
    )
    tax_authority = Field()
    okpo = Field()
    okato = Field()
    oktmo = Field()
    okfs = Field(
        input_processor=lambda x: x[0]
    )
    okfs_type = Field(
        input_processor=lambda x: x[1]
    )
    okogu = Field()
    okogu_type = Field()
    pfr = Field()
    fss = Field()
    
    file_urls = Field()
    files = Field()
    
class RusprofileLoader(ItemLoader):
    default_output_processor = TakeFirst()
    
    def load_profile(self, url):
        self.add_css("name",".company-name::text")
        self.add_css("inn",".copy_target[id=clip_inn]::text")
        self.add_css("kpp",".copy_target[id=clip_kpp]::text")
        self.add_css("ogrn",".copy_target[id=clip_ogrn]::text")
        self.add_css("reg_date",".company-info__text[itemprop=foundingDate]::text")
        address_sel = self.selector.css(".company-info__text[itemprop=address] span::text").getall()
        address = ",".join([string.strip() for string in address_sel])
        self.add_value("address", address)
        self.add_css("head",".link-arrow.gtm_main_fl span::text")
        self.add_css("head_inn",".information-text::text")
        self.add_css("capital",".company-col:contains('Уставный капитал') .company-info__text .copy_target::text")
        self.add_css("activity",".company-row:contains('Основной вид деятельности') .company-info__text::text")
        self.add_css("activity_code",".company-row:contains('Основной вид деятельности') .bolder::text")
        self.add_css("tax_authority",".company-row:contains('Налоговый орган') .company-info__text::text")
        self.add_css("okpo",".copy_target[id=clip_okpo]::text")
        self.add_css("okato",".copy_target[id=clip_okato]::text")
        self.add_css("oktmo",".copy_target[id=clip_oktmo]::text")
        self.add_css("okfs",".copy_target[id=clip_okfs]::text")
        self.add_css("okfs_type",".rightcol .company-row:contains('Коды статистики') .chief-title::text")
        self.add_css("okogu",".copy_target[id=clip_okogu]::text")
        self.add_css("okogu_type",".rightcol .company-row:contains('Коды статистики') .chief-title::text")
        
        pdf_link = self.selector.css(".btn.btn-white.btn-icon.btn-pdf-icon.gtm_main_pdf::attr(href)").get()
        file_url = ["".join((url,pdf_link))]
        self.add_value("file_urls", file_url)
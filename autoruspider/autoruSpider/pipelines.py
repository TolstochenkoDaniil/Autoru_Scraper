# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


""" class AutoruspiderPipeline(object):
    def process_item(self, item, spider):
        return item """
    
""" class TxtWriterPipeline:
    
    def open_spider(self, spider):
        self.file = open('toyota.txt', 'a',encoding='utf8')

    def close_spider(self, spider):
        self.file.close()
        
    def process_item(self, car_item, spider):
        attr_value = car_item.items()
        line=[str(value[1]) for value in attr_value]
        
        feature_row = ','.join(line) + '\n'
        self.file.write(feature_row)
        
        return car_item """
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import NotConfigured

import pyodbc as msdb

class DatabasePipeline(object):
    def __init__(self,db,user,password,host):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        
    def process_item(self, item):
        return item

    def open_spider(self, spider):
        self.conn = msdb.connect('DRIVER={ODBC DRIVER 17 for SQL Server};SERVER='+self.host+';DATABASE='+self.db+';UID='+self.user+';PWD='+self.password)
        self.cursor = self.conn.cursor()
        
    def process_item(self,item,spider):
        query = 'INSERT INTO dbo.records ()'
        self.cursor.execute(query,)
        self.conn.commit()
        
        return item
    
    def close_spider(self, spider):
        self.conn.close()
        
    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        
        if not db_settings:
            raise NotConfigured
        
        db = db_settings['db']
        user = db_settings['user']
        password = db_settings['password']
        host = db_settings['host']
        
        return cls(db,user,password,host)
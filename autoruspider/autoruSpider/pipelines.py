# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import NotConfigured

import logging
import pyodbc as msdb
import datetime
import os

class DatabasePipeline(object):
    log = os.path.join(os.getcwd(),"log","db.log")
    
    logger = logging.getLogger(__name__)

    f_handler = logging.FileHandler(log, mode='w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)
    
    def __init__(self,db,user,password,host,driver):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.driver = driver
        self.conn = None

    def open_spider(self, spider):
        self.conn = msdb.connect(self.driver+'SERVER='+self.host+';DATABASE='+self.db+';UID='+self.user+';PWD='+str(self.password))
        
        if self.conn:
            self.logger.info("Connection successfull.")
        else:
            self.logger.warning("Connection failed.")
            self.logger.warning("DataBase settings:\nuser - {}\nhost - {}\ndb - {}".format(self.user,self.host,self.db))
            
        self.cursor = self.conn.cursor()
        
    def process_item(self,item,spider):
        if self.get_id(item): 
            if item['price']:
                db_price = self.get_price(item)
                
                if (db_price > item['price']):
                    self.add_to_prices(item)
            else:
                self.add_to_prices(item)
        else:
            self.add_to_records(item)   
            self.add_to_prices(item)
            
        return item
    
    def close_spider(self, spider):
        self.conn.close()
        self.logger.info("Connection closed.")
        
    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        
        if not db_settings:
            raise NotConfigured
        
        db = db_settings['db']
        user = db_settings['user']
        password = db_settings['password']
        host = db_settings['host']
        driver = db_settings['driver']
        
        return cls(db,user,password,host,driver)
    
    def add_to_records(self, item):
        query = f'''INSERT INTO [{self.db}].[dbo].[Records] ([ID],[Title],[Distance],[Year],
                [Link],[Color],[Car_type],[Horse_power],[Engine_type],[Fuel_type],[Wheel_type],
                [Transmission],[Owner],[Area])
                VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        args = (item['ID'],item['title'],item['distance'],item['year'],
                item['link'],item['color'],item['car_type'],
                item['horse_power'],item['engine_type'],item['fuel_type'],item['wheel_type'],
                item['transmission'],item['advert'],item['area'])
        
        self.cursor.execute(query,args)
        self.conn.commit()
        self.logger.info("Added car {}.".format(item['ID']))
        
    def add_to_prices(self, item):
        ts = datetime.date.today().isoformat()
        query = f'''INSERT INTO [{self.db}].[dbo].[Prices] ([Price],[DatePriceChange],[CarID])
                VALUES
                (?,?,?)
                '''
        if item['price']:
            args = (item['price'],ts,item['ID'])
        else:
            args = (0,ts,item['ID'])
        
        self.logger.info("Added price record to {}".format(item['ID']))
        
        self.cursor.execute(query,args)
        self.conn.commit()
        
    def get_id(self, item):
        query = f'''SELECT [ID] 
                FROM [{self.db}].[dbo].[Records]
                WHERE [ID] = ?
                '''
        args = (item['ID'])
        
        self.cursor.execute(query,args)
        row = self.cursor.fetchone()
        
        try:
            return row[0]
        except TypeError:
            return None
    
    def get_price(self, item):
        query = f'''SELECT TOP 1 [Price] 
                FROM [{self.db}].[dbo].[Prices]
                WHERE [CarID] = ?
                ORDER BY [OID] DESC
                '''
        args = (item['ID'])
        
        self.cursor.execute(query,args)
        row = self.cursor.fetchone()
        
        try:
            return row[0]
        except TypeError:
            return None
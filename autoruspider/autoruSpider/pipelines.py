# -*- coding: utf-8 -*-
from scrapy.exceptions import NotConfigured
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes
from itemadapter import ItemAdapter
from scrapy.http import Request

import os
import hashlib
import logging
import datetime
import pyodbc as msdb
import socket
from io import BytesIO

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
        
class SpecPipeline(DatabasePipeline):
    '''
        PipeLine for processing SpecItems produced by `specification` spider.
    '''
    log = os.path.join(os.path.dirname(__file__),"spiders\\log","spec_db.log")
        
    def process_item(self, item, spider):
        try:
            if hasattr(spider, 'OID'):
                print("OID is passed.")
            if '_brand' in item:
                self.add_img_to_db(spider)
            if 'brand' in item:
                self.add_to_db(item, spider)
        except Exception as ex:
            self.logger.warning("Exception occured while adding item to database.\n {}".format(ex))
        finally:
            return item 
          
    def add_to_db(self, item, spider):
        query = '''INSERT TO {self.db}.[].[] (
        [Brand],[Model],[Generation],[Modification],
        [Volume],[Power],[Transmission],[Engine_type],
        [Fuel],[Wheel_type],[Acceleration],[Consumption],
        [Country],[Car_class],[Doors],[Seats],
        [Safety_rating],[Rating],
        [Length],[Width],[Heigth],[Wheel_base],[Clearance],[Front_width],[Back_width],[Wheel_size],
        [Trunk_size],[Tank_volume],[Equiped],[Full_weight],
        [Speed_num],
        [Front_suspension],[Back_suspension],[Front_brakes],[Back_brakes],
        [Max_speed],[Consumption_grade],[Eco_class],[Emission],
        [Engine_placement],[Boost_type],[Max_power],[Max_spin],
        [Cylinders],[Cylinders_num],[Cylinders_valves],[Cylinder_size],
        [Compression_ratio],[Power_type],
        [Url]
        )
        VALUES 
        (?,?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?
        ?,?,?,?,?,?,?,?,
        ?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?,
        ?)
        '''
        args = (item['brand'],item['model'],item['generation'],item['modification'],item['car_type'],
                item['volume'],item['power'],item['transmission'],item['engine_type'],
                item['fuel'],item['wheel_type'],item['acceleration'],item['consumption'],
                item['country'],item['car_class'],item['doors'],item['seats'],
                item['safety_rating'],item['rating'],
                item['length'],item['width'],item['heigth'],item['wheel_base'],item['clearance'],item['front_width'],item['back_width'],item['wheel_size'],
                item['trunk_size'],item['tank_volume'],item['equiped'],item['full_weight'],
                item['speed_num'],
                item['front_suspention'],item['back_suspention'],item['front_brakes'],item['back_brakes'],
                item['max_speed'],item['consumption_grade'],item['eco_class'],item['emission'],
                item['engine_placement'],item['boost_type'],item['max_power'],item['max_spin'],
                item['cylinders'],item['cylinders_num'],item['cylinders_valves'],item['cylinders_size'],
                item['compression_ratio'],item['power_type'],
                item['url'])
        
        self.cursor.execute(query,args)
        self.conn.commit()
        
        self.logger.info("Item {0} - {1} - {2} - {3} added to {4}".format(item['brand'],
                                                                          item['model'],
                                                                          item['generation'],
                                                                          item['modification'],
                                                                          self.db))
        
        def add_img_to_db(self, spider):
            query = '''INSERT TO {self.db}.[].[] ([ImgPath],[CarOID])
            VALUES
            (?,?)
            '''
            args = (spider.path,spider.OID)
            
class SpecImagesPipeline(ImagesPipeline):
    '''
        PipeLine for processing ImageItems produced by `specification` spider.
    '''
    log = os.path.join(os.getcwd(),"log","img.log")
    
    logger = logging.getLogger(__name__)

    f_handler = logging.FileHandler(log, mode='w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)
    
    def __init__(self, store_uri, download_func=None, settings=None):
        super().__init__(store_uri, download_func=download_func, settings=settings)
        # custom path variable
        self.path = None
    
    def get_media_requests(self, item, info):
        self.get_path(item, info)
        
        urls = ItemAdapter(item).get(self.images_urls_field, [])
        requests = [Request(u) for u in urls]
        return requests
    
    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        
        if self.path:
            return "{}/{}.jpg".format(self.path, image_guid)
        else:
            return "full/%s.jpg".format(image_guid)
    
    def get_path(self, item, info):
        '''
            Function to generate IMAGES_STORE path dynamically.\n
            @param: item, processed in the pipeline
            
            HINT: Call this function in any overridable ImagePipeline interface,
            where item is passed.
        '''
        if info.spider.path and os.path.exists(info.spider.path):
            path = os.path.join(info.spider.path,info.spider.OID)
            os.mkdir(path)
            
            return self.path
        
        elif '_brand' in item:
            try:
                self.path = '/'.join((item['_brand'],
                                item['_model'],
                                item['_generation'][0],
                                item['_car_type']))
                
            except Exception as ex:
                self.logger.warn("Exception accured while generating image store path. {}".format(ex))
                self.logger.warn("Image store path set to default value '{}\\full\\'.".format(info.spider.settings['IMAGES_STORE']))
            finally:
                return self.path
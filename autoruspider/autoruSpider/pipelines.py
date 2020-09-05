# -*- coding: utf-8 -*-
from scrapy.exceptions import NotConfigured
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes
from scrapy.utils.project import get_project_settings
from itemadapter import ItemAdapter
from scrapy.http import Request

import os
import hashlib
import logging
import datetime
import pyodbc as msdb
import socket
from io import BytesIO

##############################
### Monitor Spider section ###
##############################
           
class DatabasePipeline(object):
    log_dir = get_project_settings().get('LOG_DIR')
    log = os.path.join(log_dir,'db.log')
    
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
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
            if 'price' in item:
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
        
        args = (item.get('price',0),ts,item.get('ID'))
        # if item['price']:
        #     args = (item['price'],ts,item['ID'])
        # else:
        #     args = (0,ts,item['ID'])
        
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
                ORDER BY [ID] DESC
                '''
        args = (item['ID'])
        
        self.cursor.execute(query,args)
        row = self.cursor.fetchone()
        
        try:
            return row[0]
        except TypeError:
            return None
        
####################################
### Specification Spider section ###
####################################

class SpecPipeline(DatabasePipeline):
    '''
        PipeLine for processing SpecItems produced by `specification` spider.
    '''  
    
    def __init__(self, db, user, password, host, driver):
        super().__init__(db, user, password, host, driver)
        self.added = False      
        
    def process_item(self, item, spider):
        try:
            if hasattr(spider, 'OID'):
                self.add_item(item, spider)
        except Exception as ex:
            if 'PRIMARY KEY' or 'UNIQUE KEY' not in ex[1]:
                self.logger.warning("Exception occurred while adding item to database.\n {}".format(ex[1]))
                self.logger.warning("Item {}".format(item.get('modification')))
        finally:
            return item 
          
    def _add_spec(self, item, spider):
        query = f'''INSERT INTO [{self.db}].[dbo].[Specification] (
        [Brand],[Model],[Generation],[Modification],[CarType],
        [Volume],[HorsePower],[Transmission],[EngineType],
        [Fuel],[WheelType],[Acceleration],[Consumption],
        [Country],[CarClass],[Doors],[Seats],
        [Length],[Width],[Heigth],[WheelBase],[Clearance],[FrontWidth],[BackWidth],[WheelSize],
        [TrunkVolume],[TankVolume],[Equiped],[FullWeight],
        [SpeedNum],
        [FrontSuspension],[BackSuspension],[FrontBrakes],[BackBrakes],
        [MaxSpeed],[ConsumptionGrade],[EcoClass],[Emission],
        [EnginePlacement],[EngineVolume],[BoostType],[MaxPower],[MaxSpin],
        [Cylinders],[CylindersNum],[CylindersValves],[CylinderSize],
        [CompressionRatio],[PowerType],
        [Url],[CarOID]
        )
        VALUES 
        (?,?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,?,?,?,?,
        ?,?,?,?,
        ?,
        ?,?,?,?,
        ?,?,?,?,
        ?,?,?,?,?,
        ?,?,?,?,
        ?,?,
        ?,?)
        '''
        args = (item.get('brand',None),item.get('model',None),item.get('generation',None),item.get('modification',None),item.get('car_type',None),
                item.get('volume',None),item.get('power',None),item.get('transmission',None),item.get('engine_type',None),
                item.get('fuel',None),item.get('wheel_type',None),item.get('acceleration',None),item.get('consumption',None),
                item.get('country',None),item.get('car_class',None),item.get('doors',None),item.get('seats',None),
                item.get('length',None),item.get('width',None),item.get('heigth',None),item.get('wheel_base',None),item.get('clearance',None),
                item.get('front_width',None),item['back_width'],item.get('wheel_size',None),
                item.get('trunk_volume',None),item.get('tank_volume',None),item.get('equiped',None),item.get('full_weight',None),
                item.get('speed_num',None),
                item.get('front_suspension',None),item.get('back_suspension',None),item.get('front_brakes',None),item.get('back_brakes',None),
                item.get('max_speed',None),item.get('consumption_grade',None),item.get('eco_class',None),item.get('emissions',None),
                item.get('engine_placement',None),item.get('engine_volume',None),item.get('boost_type',None),item.get('max_power',None),item.get('max_spin',None),
                item.get('cylinders',None),item.get('cylinders_num',None),item.get('cylinders_valves',None),item.get('cylinder_size',None),
                item.get('compression_ratio',None),item.get('power_type',None),
                item.get('url',None),spider.OID)
        
        self.cursor.execute(query,args)
        self.conn.commit()
        
        self.logger.info("Item {0} - {1} - {2} - {3} - {4} added to {5}".format(item['brand'],
                                                                          item['model'],
                                                                          item['generation'],
                                                                          item['modification'],
                                                                          spider.OID,
                                                                          self.db))
        
    def _add_img_path(self, spider):
        query = f'''INSERT INTO [{self.db}].[dbo].[Image] ([ID],[ImageFile])
        VALUES
        (?,?)
        '''
        path = os.path.join(spider.custom_settings['IMAGES_STORE'],spider.path)
        args = (spider.OID,path)
        
        self.cursor.execute(query,args)
        self.conn.commit()
        
        self.logger.info("Image path {} added for OID {}".format(spider.path, spider.OID))
    
    def add_item(self, item, spider):
        if not self.added and '_brand' in item:
            self._add_img_path(spider)
            self.added = True
            
        if 'brand' in item:
            self._add_spec(item, spider)
        
class SpecImagesPipeline(ImagesPipeline):
    '''
        PipeLine for processing ImageItems produced by `specification` spider.
    '''
    log_dir = get_project_settings().get('LOG_DIR')
    log = os.path.join(log_dir,'img.log')
    
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    
    logger = logging.getLogger(__name__)

    f_handler = logging.FileHandler(log, mode='w')
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    f_handler.setFormatter(f_format)

    logger.addHandler(f_handler)
    
    def __init__(self, store_uri, download_func=None, settings=None):
        super(SpecImagesPipeline, self).__init__(store_uri, download_func=download_func, settings=settings)
        # custom path variable
        self.path = None
    
    def get_media_requests(self, item, info):     
        self.path = info.spider.path   
        
        urls = ItemAdapter(item).get(self.images_urls_field, [])
        requests = [Request(u) for u in urls]
        return requests
    
    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        
        if self.path:
            return "{}\\{}.jpg".format(self.path,image_guid)
        else:
            return "full/%s.jpg".format(image_guid)
    
    def get_path(self, item, info):
        '''
            WARNING: Method is deprecated. 
            Now `path` param attaches to spider during initialize process.
            
            Function to generate IMAGES_STORE path dynamically.\n
            @param: item, processed in the pipeline
            
            HINT: Call this function in any overridable ImagePipeline interface,
            where item is passed.
        '''
        if info.spider.path and os.path.exists(info.spider.path):
            path = os.path.join(info.spider.path,str(info.spider.OID))
            os.mkdir(path)
            
            return self.path
        
        elif '_brand' in item:
            try:
                self.path = '/'.join((item['_brand'],
                                item['_model'],
                                item['_generation'][0],
                                item['_car_type']))
                
            except Exception as ex:
                self.logger.warn("Exception occurred while generating image store path. {}".format(ex))
                self.logger.warn("Image store path set to default value '{}\\full\\'.".format(info.spider.settings['IMAGES_STORE']))
            finally:
                return self.path
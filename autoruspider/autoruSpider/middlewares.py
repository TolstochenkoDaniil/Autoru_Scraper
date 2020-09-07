# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import NotConfigured

import pyodbc as msdb

class AutoruspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class AutoruspiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        
class MonitorSpiderMiddleware(AutoruspiderSpiderMiddleware):
    '''
        Middleware for preinitialization `monitor` spider.
    '''
    def __init__(self, db, user,password,host,driver):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.driver = driver
        conn = None
    
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        
        if not db_settings:
            raise NotConfigured
        
        db = db_settings['db']
        user = db_settings['user']
        password = db_settings['password']
        host = db_settings['host']
        driver = db_settings['driver']
        
        s = cls(db,user,password,host,driver)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s
    
    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        spider.start_urls = self._get_urls_from_db(spider)
        
    def _get_urls_from_db(self,spider):
        '''
            Method to retrieve valid urls from database.
            @return: list of urls.
        '''
        # query string
        query = f'''
        SELECT DISTINCT [URL_]\n
        FROM [{self.db}].[dbo].[CarModificationsAutoUpdate]
        '''
        
        conn = msdb.connect(self.driver+'SERVER='+self.host+';DATABASE='+self.db+';UID='+self.user+';PWD='+str(self.password))
        
        if conn:
            spider.logger.info("Spider connection successfull.")
        else:
            spider.logger.warning("Connection failed.")
            spider.logger.warning("DataBase settings:\nuser - {}\nhost - {}\ndb - {}".format(self.user,self.host,self.db))
            
        cursor = conn.cursor()
        urls = cursor.execute(query).fetchall()

        conn.close()
        
        return [url[0] for url in urls]    
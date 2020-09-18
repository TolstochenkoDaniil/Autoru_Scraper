import os
import logging

from scrapy.exceptions import NotConfigured
from scrapy import signals
from scrapy.utils.project import get_project_settings

from .utils import TelegramHandler

class SetupSpiderLogging:
    def __init__(self, spider, disabled=None, enabled=None):
        self.disabled = disabled
        self.enabled = enabled
        self.spider = spider
        
    @classmethod
    def from_crawler(cls, crawler):
        
        disabled = crawler.settings.get("DISABLED_LOGGERS",None)
        enabled = crawler.settings.get("ENABLED_LOGGERS",None)
        
        ext = cls(crawler.spidercls, disabled=disabled,enabled=enabled)
        ext.setup_loggers(crawler)
        
        return ext
    
    def setup_loggers(self, crawler):
        if not crawler.settings.get('LOG_DIR'):
            raise NotConfigured
        
        log_dir = crawler.settings.get('LOG_DIR')
        self.log_file = os.path.join(log_dir,'{}.log'.format(self.spider.name))
            
        self.setup_spider_logger()
        
        if self.disabled:
            self.setup_disabled()
        if self.enabled:
            self.setup_enabled()

    def setup_spider_logger(self):
        logger = logging.getLogger(self.spider.name)
        logger.setLevel(logging.INFO)
        f_handler = logging.handlers.RotatingFileHandler(self.log_file, mode='a', maxBytes=1048576, backupCount=1)
        f_handler.setLevel(logging.INFO)
        f_format = logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        f_handler.setFormatter(f_format)

        logger.addHandler(f_handler)
        self.spider.logger = logger
        
    def setup_disabled(self):
        for logger_name in self.disabled:
            logger = logging.getLogger(logger_name)
            logger.handlers = []
        
    def setup_enabled(self):
        for logger_name in self.enabled:
            self.setup_logger(logger_name)
                
    def setup_logger(self,logger_name):
        if not logger_name == 'root':
            self.add_to_spider_logger(logger_name)
        else:
            self.setup_root()
    
    def add_to_spider_logger(self,name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = self.spider.logger.handlers[0]
        logger.handlers = []
        logger.addHandler(handler)
    
    def setup_root(self):
        logger = logging.getLogger()
        logger.setLevel(get_project_settings().get("LOG_LEVEL"))
        logger.handlers = []
        f_format = logging.Formatter(fmt=get_project_settings().get("LOG_FORMAT"))
         
        f_handler = logging.handlers.RotatingFileHandler(get_project_settings().get("LOG_FILE"),
                                                         mode='a',
                                                         maxBytes=1048576,
                                                         backupCount=1)
        f_handler.setLevel(get_project_settings().get("LOG_LEVEL"))       
        f_handler.setFormatter(f_format)

        logger.addHandler(f_handler)
        
class TelegramLogger:
    def __init__(self, spider, stats, settings):
        self.spider = spider
        self.stats = stats
        self.token = settings.get("TG_TOKEN")
        self.loggers = settings.get("TG_LOGGERS")
        self.chat_id = settings.get("TG_CHAT_ID")
        
    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.get("TG_TOKEN"):
            raise NotConfigured
        
        if not crawler.settings.get("TG_CHAT_ID"):
            raise NotConfigured
        
        ext = cls(crawler.spidercls,crawler.stats,crawler.settings)
        
        crawler.signals.connect(ext.dump_stats, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        
        ext.set_tg_bot()        
        
        return ext
    
    def dump_stats(self):
        report = f'''\
        Spider "{self.spider.name}" close reason: {self.stats.get_stats().get("finish_reason")}
        Items scraped: {self.stats.get_stats().get("item_scraped")}
        Responses received: {self.stats.get_stats().get("response_received")}
        '''
        self.logger.info(report)
    
    def item_scraped(self, spider):
        self.stats.inc_value('item_scraped',spider=spider)
        
    def response_received(self, spider):
        self.stats.inc_value('response_received',spider=spider)
        
    def set_tg_bot(self):
        if self.loggers:
            for _logger in self.loggers:
                logger = logging.getLogger(_logger)
                handler = TelegramHandler(token=self.token,chat_id=self.chat_id)
                logger.addHandler(handler)
        
        self.logger = logging.getLogger('telegram_logger')
        self.logger.setLevel(logging.INFO)    
        handler = TelegramHandler(token=self.token,chat_id=self.chat_id)
        self.logger.addHandler(handler)
# -*- coding: utf-8 -*-
from pathlib import WindowsPath
import logging
import os
from rusprofile.rusprofile.settings import RABBIT_EXCHANGE_URL, RABBIT_HEADERS
# Scrapy settings for autoruSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'autoruSpider'

SPIDER_MODULES = ['autoruSpider.spiders']
NEWSPIDER_MODULE = 'autoruSpider.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'autoruSpider (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 3.0
RANDOMIZE_DOWNLOAD_DELAY = True
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
COOKIES_DEBUG = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
}

RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429, 400]

DOWNLOAD_TIMEOUT = 15
# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   'scrapy.spidermiddlewares.depth.DepthMiddleware': None,
   'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': None,
   'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 30,
   'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 40,
   'scrapy.spidermiddlewares.referer.RefererMiddleware': 50
}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
   'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 20,
   'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 30,
   'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': None,
   'scrapy.downloadermiddlewares.stats.DownloaderStats': None,
   'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 60,
   'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 70,
   'scrapy.downloadermiddlewares.retry.RetryMiddleware': 80,
   'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
   'scrapy_selenium.SeleniumMiddleware': None,
}

REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 20
METAREFRESH_ENABLED = True
METAREFRESH_IGNORE_TAGS = []
METAREFRESH_MAXDELAY = 20

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
   'scrapy.extensions.throttle.AutoThrottle': 100,
   'scrapy.extensions.logstats.LogStats': 110,
   'scrapy.extensions.corestats.CoreStats': 120
}

STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 4.0
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 10.0
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 5.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = True

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Database settings
DB_SETTINGS = {
    'db':'z_AUTORU',
    'user':'tolstochenko_di',
    'password':123,
    'host':'192.168.2.42',
    'driver':"DRIVER={SQL Server Native Client 11.0};"
}

# Feeds settings

# Logging settings
HUB = os.environ.get("SPIDER_HUB", None)
# Logging settings
if True:
   BASE_DIR = os.path.abspath(os.path.join(HUB,BOT_NAME,BOT_NAME))
   LOG_ENABLED = True
   LOG_ENCODING = 'utf-8'
   LOG_DIR = os.path.join(BASE_DIR,'log')
   LOG_FILE = os.path.join(LOG_DIR,"launch.log")
   LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
   LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
   LOG_LEVEL = logging.ERROR
   LOG_STOUT = True
   
# services
APPRAISAL_SERVICE = 'http://127.0.0.1:8000/appraisal'
UPDATE_SERVICE = 'http://127.0.0.1:8000/update'

# RabbitMQ
RABBIT_EXCHANGE_URL = 'https://b2btest.ma.ru/NEURAL/v1/Training'
RABBIT_HEADERS = {
   "content-type": "application/json",
   "authorization": "Bearer 2EC28662F8B6F6469FD369766873E33F"
}
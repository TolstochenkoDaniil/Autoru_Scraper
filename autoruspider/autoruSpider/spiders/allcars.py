from scrapy import Spider
#from ..items import 
import pandas as pd

pd = pd.read_csv('D:\Python\Autoru_Scraper-master\autoruSpider\autoruSpider\brands.csv', sep = ',')
#print (pd)

class AllCar(Spider):
    name = "AllCar"
    allowed_domains = ['auto.ru']
    urls = pd.read_csv(r'D:\\Python\Autoru_Scraper-master\autoruSpider\autoruSpider\brands.csv', sep = ',').iloc[:,2]
    def parse (self, response):
        
        for url in self.urls:
            logger.info(url)
            for page in url:  
                yield Request(url_parse.urljoin(response.url, url))
            # parse url
        for selector in selectors:
            yield self.parse_ithem(selector, response)
             #pass
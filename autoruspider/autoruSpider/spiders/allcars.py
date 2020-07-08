from scrapy import Spider

import pandas as pd

pd = pd.read_csv('D:\Python\Autoru_Scraper-master\autoruSpider\autoruSpider\brands.csv', sep = ',')

class AllCar(Spider):
    name = "AllCar"
    allowed_domains = ['auto.ru']
    urls = pd.read_csv(r'D:\\Python\Autoru_Scraper-master\autoruSpider\autoruSpider\brands.csv', sep = ',').iloc[:,2]
    def parse (self, response):
        
        for url in self.urls:
            logger.info(url)  
            yield Request(url_parse.urljoin(response.url, url))

        for selector in selectors:
            yield self.parse_ithem(selector, response)
             #pass
            # ок
    
    
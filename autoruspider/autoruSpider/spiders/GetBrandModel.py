from scrapy import Spider
from ..items import ListBrandsModelsLoader, ListBrandsModelsItem

class GetBrand(Spider):
    name = 'ListBrandsModels'
    allowed_domains = ['auto.ru']
    start_urls = ['https://auto.ru/htmlsitemap/mark_model_catalog.html']

    def parse (self, response):

        selectors = response.xpath('/html/body/div[1]/div')
        for selector in selectors:
            yield self.parse_ithem(selector, response)
    
    
    def parse_ithem(self, selector,response):

        ListInfoBrandsModelsLoader = ListBrandsModelsLoader(item = ListBrandsModelsItem(), selector=selector)
        ListInfoBrandsModelsLoader.parse()

        return ListInfoBrandsModelsLoader.load_item()
    custom_settings = {
        'FEED_FORMAT' : 'csv',
        'FEED_URI' : 'brands.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8',
        'FEED_EXPORT_FIELDS' : ['brand','model','link']}

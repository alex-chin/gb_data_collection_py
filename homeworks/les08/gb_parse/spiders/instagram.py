import scrapy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://https://www.instagram.com/accounts/login//']

    def parse(self, response):

        pass

# -*- coding: utf-8 -*-
import scrapy


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['http://blog.jobbole.com/']
    start_urls = ['http://blog.jobbole.com/114706/']

    def parse(self, response):
        re_selector = response.xpath('// *[ @ id = "post-114706"] / div[1] / h1')
        pass

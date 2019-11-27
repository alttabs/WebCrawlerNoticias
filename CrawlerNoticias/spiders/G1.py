# -*- coding: utf-8 -*-
import scrapy


class G1Spider(scrapy.Spider):
    name = 'G1'
    allowed_domains = ['https://g1.globo.com']
    start_urls = ['http://https://g1.globo.com/politica/']


    def parse(self, response):

    
        pass

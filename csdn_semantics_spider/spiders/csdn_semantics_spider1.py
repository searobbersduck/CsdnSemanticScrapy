#coding=utf-8
import re
import json
from scrapy.selector import Selector
try:
    from scrapy.spider import Spider
except:
    from scrapy.spider import BaseSpider as Spider
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor as sle
from csdn_semantics_spider.items import *

import chardet

class CsdnSemanticsSpider(CrawlSpider):
    #定义爬虫的名称
    name = "CsdnSemanticsSpider"
    #定义允许抓取的域名,如果不是在此列表的域名则放弃抓取
    allowed_domains = ["blog.csdn.net"]
    #定义抓取的入口url
    start_urls = [
        "http://blog.csdn.net/searobbers_duck/article/details/51839799"
    ]
    # 定义爬取URL的规则，并指定回调函数为parse_item

#    rules = [
#        Rule(sle(allow=("/\S{1,}/article\details/\d{1,}")), #此处要注意?号的转换，复制过来需要对?号进行转义。
#                         follow=True,
#                         callback='parse_item')
    rules = [
        Rule(sle(allow=("/\S{1,}/article/details/\d{1,}")), #此处要注意?号的转换，复制过来需要对?号进行转义。
                         follow=True,
                         callback='parse_item')
    ]
    #print "**********CnblogsSpider**********"
    #定义回调函数
    #提取数据到Items里面，主要用到XPath和CSS选择器提取网页数据
    def parse_item(self, response):
        #print "-----------------"
        items = []
        sel = Selector(response)
        base_url = get_base_url(response)
        title = sel.css('title').xpath('text()').extract()
	key_substr=u'语义'
        for index in range(len(title)):
            item = CsdnSemanticsSpiderItem()
            item['title']=title[index]#.encode('utf-8').decode('utf-8')
            pos=item['title'].find(key_substr)
            print item['title']
            if(pos != -1):      
                #print item['title'] + "***************\r\n"
		item['title']=title[index]
                item['link']=base_url
                item['desc']=item['title']
                #print base_url + "********\n"
                items.append(item)
                #print repr(item).decode("unicode-escape") + '\n'
        return items

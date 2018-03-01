# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime

class Jingdong(scrapy.Spider):
    name = "jingdong"
    download_delay = 0.1
    def __init__(self, settings, top_num=None):
        
        self.key_words = settings['KEY_WORDS']
        self.batchno = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        if top_num:
            self.top_num = top_num
        else:
            self.top_num = 20   #默认前20个商品
    
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)
    
    def start_requests(self):
        print(self.key_words)
        for kw in self.key_words:
            kw_code = request.quote(kw)   #utf8编码
            search_url = 'https://search.jd.com/Search?keyword=%s&enc=utf-8&psort=3' % kw_code #搜索入口
            print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = search_url,
                callback = self.parse_list,
                meta = {'kw': kw}
            )
    def parse_list(self, response):
        flag = 0
        for li in response.xpath("//li[@class='gl-item']"):
            if flag < self.top_num:   #前20个商品
                if li.xpath("@data-sku"):
                    datas = {}
                    datas['srcsys'] = '京东'
                    datas['batchno'] = self.batchno
                    datas['key_word'] = response.meta['kw']
                    id = li.xpath("./@data-sku").extract()[0]
                    datas['url'] = 'http://item.jd.com/%s.html' % id
                    datas['title'] = re.sub(',|，', ' ', ''.join(li.xpath("./div/div[@class='p-name p-name-type-2']/a/em//text()").extract()))
                    print('发现第%d个%s：%s' % (flag+1, datas['key_word'], datas['title']))
                    com_url = 'http://club.jd.com/comment/productCommentSummaries.action?referenceIds=%s' % id
                    flag += 1
                    yield scrapy.http.Request(
                        url = com_url,
                        callback = self.parse_com_cont,
                        meta = {'datas': datas},
                        dont_filter = True
                    )
            else:
                break
    def parse_com_cont(self, response):
        datas = response.meta['datas']
        while not re.search('"CommentCount":(\d+)',response.text):
            yield scrapy.http.Request(
                        url = response.url,
                        callback = self.parse_com_cont,
                        meta = {'datas': datas},
                        dont_filter = True
                    )
        datas['com_cnt'] = re.search('"CommentCount":(\d+)',response.text).group(1)
        print('评论数：' + datas['com_cnt'])
        yield datas

            
    
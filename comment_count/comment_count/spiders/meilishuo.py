# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime

class Meilishuo(scrapy.Spider):
    name = "meilishuo"
    # download_delay = 1
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
            search_url = 'http://www.meilishuo.com/search/goods/?searchKey=%s' % kw_code #搜索入口
            print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = search_url,
                callback = self.parse_list,
                meta = {'kw': kw}
            )
    def parse_list(self, response):
        flag = 0
        for li in response.xpath("//ul[@id='product-ul']//li[@class='product-list fl cparams_acms_iids']"):
            if flag < self.top_num:   #前20个商品
                datas = {}
                datas['srcsys'] = '美丽说'
                datas['batchno'] = self.batchno
                datas['key_word'] = response.meta['kw']
                datas['url'] =  li.xpath(".//a[@class='text-link']/@href").extract()[0]
                datas['title'] = re.sub(',|，', ' ', ''.join(li.xpath(".//a[@class='text-link']//text()").extract())).strip()
                print('发现第%d个%s：%s' % (flag+1, datas['key_word'], datas['title']))
                flag += 1
                yield scrapy.http.Request(
                    url = datas['url'],
                    callback = self.parse_com_cont,
                    meta = {'datas': datas},
                    # dont_filter = True
                )
            else:
                break
    def parse_com_cont(self, response):
        datas = response.meta['datas']
        try:
            datas['com_cnt'] = re.search('累计评价.*?<em>(\d+)</em>', response.text, re.S).group(1)
        except:
            datas['com_cnt'] = '0'
        print('评论数：' + datas['com_cnt'])
        yield datas

            
    
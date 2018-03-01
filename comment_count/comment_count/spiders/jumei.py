# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime

class Jumei(scrapy.Spider):
    name = "jumei"
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
            search_url = 'http://search.jumei.com/?filter=0-41-1&search=%s' % kw_code #搜索入口
            print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = search_url,
                callback = self.parse_list,
                meta = {'kw': kw}
            )
    def parse_list(self, response):
        flag = 0
        for li in response.xpath("//div[@class='products_wrap']/ul/li"):
            if flag < self.top_num:   #前20个商品
                datas = {}
                datas['srcsys'] = '聚美优品'
                datas['batchno'] = self.batchno
                datas['key_word'] = response.meta['kw']
                id = li.xpath("./@pid").extract()[0]
                datas['title'] = re.sub('\u2022|\xa0|,|，', ' ', ''.join(li.xpath(".//div[@class='s_l_name']/a//text()").extract())).strip()
                # print(title)
                datas['url'] = li.xpath(".//div[@class='s_l_name']/a/@href").extract()[0]
                print(u'发现第%d个%s：%s' % (flag+1, datas['key_word'], datas['title']))
                com_url = 'http://koubei.jumei.com/ajax/reports_for_deal_page.json?product_id=%s' % id
                flag += 1
                # print(datas)
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
        try:
            datas['com_cnt'] = re.search('"comments_count":"(\d+)"', response.text).group(1)
        except:
            datas['com_cnt'] = '0'
        try:
            datas['product_id_new'] = re.search('"product_id_new":"(\w+)"', response.text).group(1)
        except:
            datas['product_id_new'] = ''
        print('评论数：' + datas['com_cnt'])
        
        yield datas

            
    
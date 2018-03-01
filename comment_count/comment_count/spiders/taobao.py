# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime
import json

class Taobao(scrapy.Spider):
    name = "taobao"
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
        for kw in self.key_words[:2]:
            kw_code = request.quote(kw)   #utf8编码
            # https://s.taobao.com/search?q=%E7%9C%BC%E9%9C%9C&bcoffset=4&s=132
            search_url = 'https://s.taobao.com/search?q=%s' % kw_code #搜索入口
            print(u'开始搜索' + kw)
            yield scrapy.http.Request(
                url = search_url,
                callback = self.parse_list,
                meta = {'kw': kw}
            )
    def parse_list(self, response):
        data = re.findall('g_page_config = ({.*?});', response.text)[0]  #源码匹配商品json
        data = json.loads(data) #json转字典
        flag = 0
        for item in data['mods']['itemlist']['data']['auctions']:
            if flag < self.top_num:   #前20个商品
                if not item['shopcard']['isTmall']:
                    datas = {}
                    datas['srcsys'] = '淘宝'
                    datas['batchno'] = self.batchno
                    datas['key_word'] = response.meta['kw']
                    datas['url'] =  response.urljoin(item['detail_url'])
                    datas['title'] = re.sub('<.*?>|,|，|\u2728|\u2022|\xa0', '', item['title'])
                    print('发现第%d个%s：%s' % (flag+1, datas['key_word'], datas['title']))
                    com_url = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=%s' % item['nid']
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
        datas['com_cnt'] = re.search('"rateTotal":(\d+)', response.text).group(1)
        print('评论数：' + datas['com_cnt'])
        yield datas

            
    
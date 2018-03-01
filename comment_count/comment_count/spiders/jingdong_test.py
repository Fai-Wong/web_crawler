# -*- coding:utf8 -*-
import re
from urllib import request
import scrapy
import datetime
import json


class Jingdong(scrapy.Spider):
    name = "jingdong_test"
    download_delay = 0.1
    custom_settings = {
        'USER_AGENT':'Mozilla/5.0 (Linux; U;Android 2.3.5;zh-cn;P331Build/GRJ22) AppleWebKit/533.1 (KHTML,like Gecko) Version/4.0 Mobile Safari/533.1'
    }
    def __init__(self, page_count=None, *args, **kwargs):
        super(Jingdong, self).__init__(*args, **kwargs)
        # self.key_words = settings['KEY_WORDS']
        self.batchno = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        #手机版一页10个，乘多个6即等于pc版
        if page_count:
            self.page_count = page_count * 6
        else:
            self.page_count = 5 * 6

    # @classmethod
    # def from_crawler(cls, crawler):
        # settings = crawler.settings
        # return cls(settings)
    
    def start_requests(self):
        # print(self.key_words)
        for kw in open('key_words.txt'):
            kw = kw.strip()
            for i in range(1,int(self.page_count)+1):
                url = 'https://so.m.jd.com/ware/searchList.action'
                print(u'开始搜索' + kw)
                formdata = {'_format_':'json','keyword':kw,'page':str(i),'sort':''}
                yield scrapy.http.FormRequest(
                    url = url,
                    formdata = formdata,
                    callback = self.parse_list,
                    meta = {'kw': kw}
                )
            # break
    def parse_list(self, response):

        print(response.status)
        
        jsondata = re.findall(r'"wareList\\":(\[.*?\])\}', response.text)[0].replace(r'\\\"', '#').replace(r'\"', '"')
        
        for d in json.loads(jsondata):
                datas = {}
                datas['srcsys'] = '京东'
                datas['batchno'] = self.batchno
                datas['key_word'] = response.meta['kw']
                datas['product_id'] = d['wareId']
                datas['url'] = 'http://item.jd.com/%s.html' % datas['product_id']
                datas['title'] = d['wname']
                print('发现%s：%s' % (datas['key_word'], datas['title']))
                datas['com_cnt'] = d['totalCount']
                yield datas
                

            
    